#!/usr/bin/env bash
set -e

# ==========================================
# PREPARATION & CLEANUP
# ==========================================
echo "--- Cleaning up previous HDFS & Local data ---"
hdfs dfs -rm -r -f /input /output || true
rm -rf /project/outputs/*
mkdir -p /project/outputs/job1 /project/outputs/job2 /project/outputs/job3 /project/outputs/job4 /project/outputs/final
hdfs dfs -mkdir -p /input/nginx /input/service_logs /input/job2 /input/job3

# ==========================================
# JOB 1: PARSE AND CLEAN
# ==========================================
echo "--- [JOB 1] Uploading raw logs to HDFS ---"
# Upload the Nginx logs directly from the PVC root
hdfs dfs -put -f /project/data/nginx_access.log /input/nginx/

# Safely handle missing service logs by creating a dummy file if they don't exist
if ls /project/data/service_logs/*.log >/dev/null 2>&1; then
    echo "--- Found service logs, uploading ---"
    hdfs dfs -put -f /project/data/service_logs/*.log /input/service_logs/
else
    echo "--- No service logs found on PVC, creating dummy file to prevent Hadoop crash ---"
    touch /tmp/dummy_service.log
    hdfs dfs -put -f /tmp/dummy_service.log /input/service_logs/
fi

echo "--- [JOB 1] Executing MapReduce ---"
hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
    -files /project/mapreduce/job1/map.py,/project/mapreduce/job1/reduce.py \
    -mapper "python3 map.py" \
    -reducer "python3 reduce.py" \
    -input /input/nginx,/input/service_logs \
    -output /output/job1

echo "--- [JOB 1] Extracting Outputs locally ---"
hdfs dfs -cat /output/job1/part-* > /project/outputs/job1/all_parsed.tsv
# Use || true to prevent set -e from crashing if grep finds nothing
grep "^NGINX" /project/outputs/job1/all_parsed.tsv | cut -f2- > /project/outputs/job1/cleaned_nginx_logs.csv || true
grep "^SERVICE" /project/outputs/job1/all_parsed.tsv | cut -f2- > /project/outputs/job1/cleaned_service_logs.csv || true
grep "^INVALID" /project/outputs/job1/all_parsed.tsv | cut -f2- > /project/outputs/job1/invalid_logs.csv || true

# Ensure files exist for the next jobs even if they are empty
touch /project/outputs/job1/cleaned_nginx_logs.csv
touch /project/outputs/job1/cleaned_service_logs.csv

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
grep "^SERVICE_FINAL" /project/outputs/job2/all_stats.tsv | cut -f2- > /project/outputs/job2/service_stats.csv || true
grep "^ENDPOINT_FINAL" /project/outputs/job2/all_stats.tsv | cut -f2- > /project/outputs/job2/endpoint_stats.csv || true
grep "^SCENARIO_FINAL" /project/outputs/job2/all_stats.tsv | cut -f2- > /project/outputs/job2/scenario_stats.csv || true

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
grep "^TEAM_REQ" /project/outputs/job3/all_counts.tsv | cut -f2- > /project/outputs/job3/country_team_requests.csv || true
grep "^MATCH_REQ" /project/outputs/job3/all_counts.tsv | cut -f2- > /project/outputs/job3/country_matchday_requests.csv || true
grep "^STADIUM_REQ" /project/outputs/job3/all_counts.tsv | cut -f2- > /project/outputs/job3/country_stadium_requests.csv || true

# ==========================================
# JOB 4: POPULAR ENTITY BY COUNTRY
# ==========================================
echo "--- [JOB 4] Executing MapReduce ---"
hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
    -files /project/mapreduce/job4/map.py,/project/mapreduce/job4/reduce.py \
    -mapper "python3 map.py" \
    -reducer "python3 reduce.py" \
    -input /output/job3 \
    -output /output/job4

echo "--- [JOB 4] Extracting Outputs locally ---"
hdfs dfs -cat /output/job4/part-* > /project/outputs/job4/all_popular.tsv
grep "^TEAM_POP" /project/outputs/job4/all_popular.tsv | cut -f2- > /project/outputs/job4/popular_team_by_country.csv || true
grep "^MATCH_POP" /project/outputs/job4/all_popular.tsv | cut -f2- > /project/outputs/job4/popular_matchday_by_country.csv || true
grep "^STADIUM_POP" /project/outputs/job4/all_popular.tsv | cut -f2- > /project/outputs/job4/popular_stadium_by_country.csv || true

# ==========================================
# JOB 5: FINAL REPORT GENERATION
# ==========================================
echo "--- [JOB 5] Executing MapReduce ---"
hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
    -D mapreduce.job.reduces=1 \
    -files /project/mapreduce/job5/map.py,/project/mapreduce/job5/reduce.py \
    -mapper "python3 map.py" \
    -reducer "python3 reduce.py" \
    -input /output/job2,/output/job3,/output/job4 \
    -output /output/job5

echo "--- [JOB 5] Extracting Final Summary JSON ---"

hdfs dfs -cat /output/job5/part-* > /project/outputs/final/summary.json

echo "--- Full MapReduce Pipeline Complete! ---"
echo "Check /project/outputs/final/summary.json for your final results!"