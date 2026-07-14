import argparse
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, when, regexp_extract, avg, count, desc, window
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType

def start_world_cup_streaming(input_path, checkpoint_path):
    os.makedirs(input_path, exist_ok=True)

    spark = SparkSession.builder \
        .appName("WorldCupLiveAnalytics") \
        .master("local[*]") \
        .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    nginx_schema = StructType([
        StructField("timestamp", StringType(), True),
        StructField("request_id", StringType(), True),
        StructField("client_ip", StringType(), True),
        StructField("client_country", StringType(), True),
        StructField("scenario", StringType(), True),
        StructField("method", StringType(), True),
        StructField("path", StringType(), True),
        StructField("service", StringType(), True),
        StructField("status_code", IntegerType(), True),
        StructField("request_time_sec", StringType(), True),
        StructField("user_agent", StringType(), True)
    ])

    raw_stream = spark.readStream \
        .schema(nginx_schema) \
        .json(input_path)

    # 1. Cast types and handle time
    # 2. FIX: Only extract team names if the path actually hits the teams API
    parsed_stream = raw_stream \
        .withColumn("event_time", col("timestamp").cast(TimestampType())) \
        .withColumn("latency", col("request_time_sec").cast(DoubleType())) \
        .withColumn("is_error", when(col("status_code") >= 400, 1).otherwise(0)) \
        .withColumn("queried_team", 
                    when(col("path").contains("/api/teams"), regexp_extract(col("path"), r"name=([^&]+)", 1))
                    .otherwise(""))

    # Add watermark to handle delayed data and prevent memory leaks over time
    watermarked_stream = parsed_stream.withWatermark("event_time", "1 minute")

    # Metric Req A, B & E: Live counts, latency, and errors grouped by 10-SECOND WINDOWS
    performance_metrics = watermarked_stream \
        .groupBy(window(col("event_time"), "10 seconds"), "service") \
        .agg(
            count("request_id").alias("live_request_count"),
            avg("latency").alias("avg_response_time_sec"),
            (count(when(col("is_error") == 1, True)) / count("request_id")).alias("live_error_rate")
        ) \
        .orderBy(desc("window"), desc("live_request_count"))

    # Metric Req C: High traffic endpoints in 10-second windows
    traffic_endpoints = watermarked_stream \
        .groupBy(window(col("event_time"), "10 seconds"), "path") \
        .count() \
        .orderBy(desc("window"), desc("count"))

    # Metric Req D: Popular teams by country (filtering out empty/stadium queries)
    popular_teams_country = watermarked_stream \
        .filter(col("queried_team") != "") \
        .groupBy(window(col("event_time"), "10 seconds"), "client_country", "queried_team") \
        .count() \
        .orderBy(desc("window"), desc("count"))

    # --- SINKS ---
    # Trigger processing every 10 seconds as required by project.md
    
    query_perf = performance_metrics.writeStream \
        .outputMode("complete") \
        .format("console") \
        .option("truncate", "false") \
        .option("checkpointLocation", f"{checkpoint_path}/performance") \
        .trigger(processingTime='10 seconds') \
        .start()

    query_endpoints = traffic_endpoints.writeStream \
        .outputMode("complete") \
        .format("console") \
        .option("truncate", "false") \
        .option("checkpointLocation", f"{checkpoint_path}/endpoints") \
        .trigger(processingTime='10 seconds') \
        .start()

    query_teams = popular_teams_country.writeStream \
        .outputMode("complete") \
        .format("console") \
        .option("truncate", "false") \
        .option("checkpointLocation", f"{checkpoint_path}/demographics") \
        .trigger(processingTime='10 seconds') \
        .start()

    query_perf.awaitTermination()
    query_endpoints.awaitTermination()
    query_teams.awaitTermination()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="data/stream/nginx")
    parser.add_argument("--checkpoint", type=str, default="checkpoints/spark")
    args = parser.parse_args()

    start_world_cup_streaming(input_path=args.input, checkpoint_path=args.checkpoint)