#!/usr/bin/env python3
import sys

current_key = None
total_req = 0
total_success = 0
total_4xx = 0
total_5xx = 0
total_time = 0.0

def emit(key, t_req, t_success, t_4xx, t_5xx, t_time):
    if key.startswith("SERVICE_STAT_"):
        svc = key.replace("SERVICE_STAT_", "")
        err_rate = (t_4xx + t_5xx) / float(t_req) if t_req > 0 else 0.0
        avg_time = t_time / float(t_req) if t_req > 0 else 0.0
        # Output: service, total_requests, success, 4xx, 5xx, error_rate, avg_time_ms
        out = "{},{},{},{},{},{:.4f},{:.2f}".format(svc, t_req, t_success, t_4xx, t_5xx, err_rate, avg_time)
        print("SERVICE_FINAL\t{}".format(out))
        
    elif key.startswith("ENDPOINT_STAT_"):
        ep = key.replace("ENDPOINT_STAT_", "")
        avg_time = t_time / float(t_req) if t_req > 0 else 0.0
        # Output: endpoint, total_requests, avg_time_ms
        out = "{},{},{:.2f}".format(ep, t_req, avg_time)
        print("ENDPOINT_FINAL\t{}".format(out))
        
    elif key.startswith("SCENARIO_STAT_"):
        scen = key.replace("SCENARIO_STAT_", "")
        # Output: scenario, total_requests
        out = "{},{}".format(scen, t_req)
        print("SCENARIO_FINAL\t{}".format(out))

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
        
    key, val_str = line.split('\t', 1)
    vals = val_str.split(',')
    
    if current_key == key:
        total_req += int(vals[0])
        if key.startswith("SERVICE_STAT_"):
            total_success += int(vals[1])
            total_4xx += int(vals[2])
            total_5xx += int(vals[3])
            total_time += float(vals[4])
        elif key.startswith("ENDPOINT_STAT_"):
            total_time += float(vals[1])
    else:
        if current_key:
            emit(current_key, total_req, total_success, total_4xx, total_5xx, total_time)
        
        current_key = key
        total_req = int(vals[0])
        if key.startswith("SERVICE_STAT_"):
            total_success = int(vals[1])
            total_4xx = int(vals[2])
            total_5xx = int(vals[3])
            total_time = float(vals[4])
        elif key.startswith("ENDPOINT_STAT_"):
            total_time = float(vals[1])
            total_success = 0
            total_4xx = 0
            total_5xx = 0
        elif key.startswith("SCENARIO_STAT_"):
            total_time = 0.0
            total_success = 0
            total_4xx = 0
            total_5xx = 0

if current_key:
    emit(current_key, total_req, total_success, total_4xx, total_5xx, total_time)