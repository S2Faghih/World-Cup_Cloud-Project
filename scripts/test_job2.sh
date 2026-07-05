#!/usr/bin/env bash
set -e

# ==========================================
# PREPARATION & CLEANUP
# ==========================================
echo "--- Cleaning up previous HDFS & Local data ---"
hdfs dfs -rm -r -f /input
hdfs dfs -rm -r -f /output
rm -rf /project/outputs/job1 /project/outputs/job2
mkdir -p /project/outputs/job1 /project/outputs/job2
hdfs dfs -mkdir -p /input/nginx /input/service_logs /input/job2

# ==========================================
# JOB 1: PARSE AND CLEAN
# ==========================================
echo "--- Uploading raw logs to HDFS for Job 1 ---"
hdfs dfs -put -f /project/data/nginx/nginx_access.log /input/nginx/
hdfs dfs -put -f /project/data/service_logs/*.log /input/service_logs/

echo "--- Executing Job 1 ---"
hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
    -files /project/mapreduce/job1/map.py,/project/mapreduce/job1/reduce.py \
    -mapper "python3 map.py" \
    -reducer "python3 reduce.py" \
    -input /input/nginx,/input/service_logs \
    -output /output/job1

echo "--- Extracting Job 1 Outputs locally ---"
hdfs dfs -cat /output/job1/part-* > /project/outputs/job1/all_parsed.tsv
grep "^NGINX" /project/outputs/job1/all_parsed.tsv | cut -f2- > /project/outputs/job1/cleaned_nginx_logs.csv
grep "^SERVICE" /project/outputs/job1/all_parsed.tsv | cut -f2- > /project/outputs/job1/cleaned_service_logs.csv
grep "^INVALID" /project/outputs/job1/all_parsed.tsv | cut -f2- > /project/outputs/job1/invalid_logs.csv

# ==========================================
# JOB 2: GENERAL NGINX AGGREGATION
# ==========================================
echo "--- Uploading cleaned Nginx logs to HDFS for Job 2 ---"
hdfs dfs -put -f /project/outputs/job1/cleaned_nginx_logs.csv /input/job2/

echo "--- Executing Job 2 ---"
hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
    -files /project/mapreduce/job2/map.py,/project/mapreduce/job2/reduce.py \
    -mapper "python3 map.py" \
    -reducer "python3 reduce.py" \
    -input /input/job2/cleaned_nginx_logs.csv \
    -output /output/job2

echo "--- Extracting Job 2 Outputs locally ---"
hdfs dfs -cat /output/job2/part-* > /project/outputs/job2/all_stats.tsv
grep "^SERVICE_FINAL" /project/outputs/job2/all_stats.tsv | cut -f2- > /project/outputs/job2/service_stats.csv
grep "^ENDPOINT_FINAL" /project/outputs/job2/all_stats.tsv | cut -f2- > /project/outputs/job2/endpoint_stats.csv
grep "^SCENARIO_FINAL" /project/outputs/job2/all_stats.tsv | cut -f2- > /project/outputs/job2/scenario_stats.csv

echo "--- Pipeline Complete! ---"