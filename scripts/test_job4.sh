#!/usr/bin/env bash
set -e

# ==========================================
# PREPARATION & CLEANUP
# ==========================================
echo "--- Cleaning up previous HDFS & Local data ---"
hdfs dfs -rm -r -f /input
hdfs dfs -rm -r -f /output
rm -rf /project/outputs/job1 /project/outputs/job2 /project/outputs/job3 /project/outputs/job4
mkdir -p /project/outputs/job1 /project/outputs/job2 /project/outputs/job3 /project/outputs/job4
hdfs dfs -mkdir -p /input/nginx /input/service_logs /input/job2 /input/job3

# ==========================================
# JOB 1: PARSE AND CLEAN
# ==========================================
echo "--- [JOB 1] Uploading raw logs to HDFS ---"
hdfs dfs -put -f /project/data/nginx/nginx_access.log /input/nginx/
hdfs dfs -put -f /project/data/service_logs/*.log /input/service_logs/

echo "--- [JOB 1] Executing MapReduce ---"
hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
    -files /project/mapreduce/job1/map.py,/project/mapreduce/job1/reduce.py \
    -mapper "python3 map.py" \
    -reducer "python3 reduce.py" \
    -input /input/nginx,/input/service_logs \
    -output /output/job1

echo "--- [JOB 1] Extracting Outputs locally ---"
hdfs dfs -cat /output/job1/part-* > /project/outputs/job1/all_parsed.tsv
grep "^NGINX" /project/outputs/job1/all_parsed.tsv | cut -f2- > /project/outputs/job1/cleaned_nginx_logs.csv
grep "^SERVICE" /project/outputs/job1/all_parsed.tsv | cut -f2- > /project/outputs/job1/cleaned_service_logs.csv
grep "^INVALID" /project/outputs/job1/all_parsed.tsv | cut -f2- > /project/outputs/job1/invalid_logs.csv

# ==========================================
# JOB 2: GENERAL NGINX AGGREGATION
# ==========================================
echo "--- [JOB 2] Uploading cleaned Nginx logs to HDFS ---"
hdfs dfs -put -f /project/outputs/job1/cleaned_nginx_logs.csv /input/job2/

echo "--- [JOB 2] Executing MapReduce ---"
hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
    -files /project/mapreduce/job2/map.py,/project/mapreduce/job2/reduce.py \
    -mapper "python3 map.py" \
    -reducer "python3 reduce.py" \
    -input /input/job2/cleaned_nginx_logs.csv \
    -output /output/job2

echo "--- [JOB 2] Extracting Outputs locally ---"
hdfs dfs -cat /output/job2/part-* > /project/outputs/job2/all_stats.tsv
grep "^SERVICE_FINAL" /project/outputs/job2/all_stats.tsv | cut -f2- > /project/outputs/job2/service_stats.csv
grep "^ENDPOINT_FINAL" /project/outputs/job2/all_stats.tsv | cut -f2- > /project/outputs/job2/endpoint_stats.csv
grep "^SCENARIO_FINAL" /project/outputs/job2/all_stats.tsv | cut -f2- > /project/outputs/job2/scenario_stats.csv

# ==========================================
# JOB 3: COUNTRY-ENTITY REQUEST COUNT
# ==========================================
echo "--- [JOB 3] Uploading cleaned Service logs to HDFS ---"
hdfs dfs -put -f /project/outputs/job1/cleaned_service_logs.csv /input/job3/

echo "--- [JOB 3] Executing MapReduce ---"
hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
    -files /project/mapreduce/job3/map.py,/project/mapreduce/job3/reduce.py \
    -mapper "python3 map.py" \
    -reducer "python3 reduce.py" \
    -input /input/job3/cleaned_service_logs.csv \
    -output /output/job3

echo "--- [JOB 3] Extracting Outputs locally ---"
hdfs dfs -cat /output/job3/part-* > /project/outputs/job3/all_counts.tsv
grep "^TEAM_REQ" /project/outputs/job3/all_counts.tsv | cut -f2- > /project/outputs/job3/country_team_requests.csv
grep "^MATCH_REQ" /project/outputs/job3/all_counts.tsv | cut -f2- > /project/outputs/job3/country_matchday_requests.csv
grep "^STADIUM_REQ" /project/outputs/job3/all_counts.tsv | cut -f2- > /project/outputs/job3/country_stadium_requests.csv

# ==========================================
# JOB 4: POPULAR ENTITY BY COUNTRY
# ==========================================
echo "--- [JOB 4] Executing MapReduce (Reading directly from Job 3 HDFS output) ---"
hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
    -files /project/mapreduce/job4/map.py,/project/mapreduce/job4/reduce.py \
    -mapper "python3 map.py" \
    -reducer "python3 reduce.py" \
    -input /output/job3 \
    -output /output/job4

echo "--- [JOB 4] Extracting Outputs locally ---"
mkdir -p /project/outputs/job4
hdfs dfs -cat /output/job4/part-* > /project/outputs/job4/all_popular.tsv
grep "^TEAM_POP" /project/outputs/job4/all_popular.tsv | cut -f2- > /project/outputs/job4/popular_team_by_country.csv
grep "^MATCH_POP" /project/outputs/job4/all_popular.tsv | cut -f2- > /project/outputs/job4/popular_matchday_by_country.csv
grep "^STADIUM_POP" /project/outputs/job4/all_popular.tsv | cut -f2- > /project/outputs/job4/popular_stadium_by_country.csv

echo "--- Full Pipeline Complete! ---"