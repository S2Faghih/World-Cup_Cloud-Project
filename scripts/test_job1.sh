#!/usr/bin/env bash
set -e

echo "--- 1. Cleaning up previous test data ---"
hdfs dfs -rm -r -f /input
hdfs dfs -rm -r -f /output/job1

echo "--- 2. Creating HDFS input directories ---"
hdfs dfs -mkdir -p /input/nginx
hdfs dfs -mkdir -p /input/service_logs

echo "--- 3. Uploading raw logs to HDFS ---"
hdfs dfs -put -f /project/data/nginx/nginx_access.log /input/nginx/
hdfs dfs -put -f /project/data/service_logs/*.log /input/service_logs/

echo "--- 4. Executing Hadoop Streaming for Job 1 ---"
hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
    -files /project/mapreduce/job1/map.py,/project/mapreduce/job1/reduce.py \
    -mapper "python3 map.py" \
    -reducer "python3 reduce.py" \
    -input /input/nginx,/input/service_logs \
    -output /output/job1

echo "--- 5. Fetching and splitting outputs locally ---"
mkdir -p /project/outputs/job1
hdfs dfs -cat /output/job1/part-* > /project/outputs/job1/all_parsed.tsv

grep "^NGINX" /project/outputs/job1/all_parsed.tsv | cut -f2- > /project/outputs/job1/cleaned_nginx_logs.csv
grep "^SERVICE" /project/outputs/job1/all_parsed.tsv | cut -f2- > /project/outputs/job1/cleaned_service_logs.csv
grep "^INVALID" /project/outputs/job1/all_parsed.tsv | cut -f2- > /project/outputs/job1/invalid_logs.csv

echo "--- Job 1 Complete! ---"
echo "Check /project/outputs/job1/ for your CSV files."