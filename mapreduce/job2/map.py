#!/usr/bin/env python3
import sys

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    parts = line.split(',')
    
    if len(parts) != 10:
        continue
    
    scenario = parts[3]
    service = parts[4]
    path = parts[6]
    
    try:
        status_code = int(parts[7])
        request_time_ms = float(parts[8])
    except ValueError:
        continue
        
    # Categorize status codes
    success = 1 if 200 <= status_code < 300 else 0
    err4xx = 1 if 400 <= status_code < 500 else 0
    err5xx = 1 if 500 <= status_code < 600 else 0
    
    # Emit Service Stats
    # Key: SERVICE_STAT_<service> | Value: 1,success,4xx,5xx,time_ms
    print("SERVICE_STAT_{}\t{},{},{},{},{}".format(service, 1, success, err4xx, err5xx, request_time_ms))
    
    # Emit Endpoint Stats
    # Key: ENDPOINT_STAT_<path> | Value: 1,time_ms
    print("ENDPOINT_STAT_{}\t{},{}".format(path, 1, request_time_ms))
    
    # Emit Scenario Stats
    # Key: SCENARIO_STAT_<scenario> | Value: 1
    print("SCENARIO_STAT_{}\t{}".format(scenario, 1))