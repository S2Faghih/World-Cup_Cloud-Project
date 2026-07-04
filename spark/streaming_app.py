import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, when, regexp_extract, avg, count, desc
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType

def start_world_cup_streaming(input_path, checkpoint_path):
    # Initialize PySpark Session optimized for multi-core processing inside Docker
    spark = SparkSession.builder \
        .appName("WorldCupLiveAnalytics") \
        .master("local[*]") \
        .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
        .getOrCreate()

    # Lower logging verbosity to clean up the output terminal screen
    spark.sparkContext.setLogLevel("WARN")

    # Schema configuration mapping perfectly to your nginx.conf json_logs format
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

    # Instantiate the streaming source for incoming micro-batch files
    raw_stream = spark.readStream \
        .schema(nginx_schema) \
        .json(input_path)

    # Clean data & cast types safely
    # WARNING FIX: Explicitly casting request_time_sec to DoubleType to bypass null values
    parsed_stream = raw_stream \
        .withColumn("event_time", col("timestamp").cast(TimestampType())) \
        .withColumn("latency", col("request_time_sec").cast(DoubleType())) \
        .withColumn("is_error", when(col("status_code") >= 400, 1).otherwise(0)) \
        .withColumn("queried_team", regexp_extract(col("path"), r"name=([^&]+)", 1))

    # Metric Requirement A, B & E: Request counts, live error rate, and average response time
    performance_metrics = parsed_stream \
        .groupBy("service") \
        .agg(
            count("request_id").alias("live_request_count"),
            avg("latency").alias("avg_response_time_sec"),
            (count(when(col("is_error") == 1, True)) / count("request_id")).alias("live_error_rate")
        )

    # Metric Requirement C: High traffic endpoints/paths monitored in real-time
    traffic_endpoints = parsed_stream \
        .groupBy("path") \
        .count() \
        .sort(desc("count"))

    # Metric Requirement D: Most popular queried team by country in the live data stream
    popular_teams_country = parsed_stream \
        .filter(col("queried_team") != "") \
        .groupBy("client_country", "queried_team") \
        .count() \
        .sort(desc("count"))

    # Console Sink for Performance Metrics (Volume, Latency, Error Rates)
    query_perf = performance_metrics.writeStream \
        .outputMode("complete") \
        .format("console") \
        .option("checkpointLocation", f"{checkpoint_path}/performance") \
        .start()

    # Console Sink for Live High-Traffic Endpoints
    query_endpoints = traffic_endpoints.writeStream \
        .outputMode("complete") \
        .format("console") \
        .option("checkpointLocation", f"{checkpoint_path}/endpoints") \
        .start()

    # Console Sink for Fan Demographics (Popular Teams by Country Breakdown)
    query_teams = popular_teams_country.writeStream \
        .outputMode("complete") \
        .format("console") \
        .option("checkpointLocation", f"{checkpoint_path}/demographics") \
        .start()

    # Maintain live streaming active threads
    query_perf.awaitTermination()
    query_endpoints.awaitTermination()
    query_teams.awaitTermination()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spark Structured Streaming World Cup Analytics Engine")
    parser.add_argument("--input", type=str, default="data/stream/nginx", help="Streaming batch directory")
    parser.add_argument("--checkpoint", type=str, default="checkpoints/spark", help="Checkpoint directory")
    args = parser.parse_args()

    start_world_cup_streaming(input_path=args.input, checkpoint_path=args.checkpoint)