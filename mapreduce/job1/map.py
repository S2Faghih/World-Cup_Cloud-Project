#!/usr/bin/env python3
import sys

NGINX_FIELDS = ["timestamp", "request_id", "client_country", "scenario", "service", "method", "path", "status_code", "request_time_sec", "user_agent"]
SERVICE_FIELDS = ["timestamp", "request_id", "client_country", "service", "endpoint", "entity_type", "entity_value", "status_code", "processing_time_ms", "event_type"]

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
        
    try:
        # Parse the dictionary string 
        record = eval(line)
        
        # 1. Check if the record is an Nginx log
        if "request_time_sec" in record and "method" in record:
            if not all(field in record for field in NGINX_FIELDS):
                print("INVALID\t{}".format(line))
                continue
                
            # Validate numeric fields and convert request_time_sec to request_time_ms
            status_code = int(record["status_code"])
            request_time_ms = int(float(record["request_time_sec"]) * 1000)
            
            # Format to the fixed Nginx schema
            csv_out = "{},{},{},{},{},{},{},{},{},{}".format(
                record["timestamp"], record["request_id"], record["client_country"], 
                record["scenario"], record["service"], record["method"], 
                record["path"], status_code, request_time_ms, record["user_agent"]
            )
            print("NGINX\t{}".format(csv_out))
            
        # 2. Check if the record is a Service log
        elif "processing_time_ms" in record and "endpoint" in record:
            if not all(field in record for field in SERVICE_FIELDS):
                print("INVALID\t{}".format(line))
                continue
                
            # Validate numeric fields
            status_code = int(record["status_code"])
            processing_time_ms = int(record["processing_time_ms"])

            # Check if entity_value is completely empty or just whitespace
            if not str(record["entity_value"]).strip():
                print("INVALID\t{}".format(line))
                continue
            
            # Format to the fixed Service schema, retaining entity_type and entity_value
            csv_out = "{},{},{},{},{},{},{},{},{},{}".format(
                record["timestamp"], record["request_id"], record["client_country"], 
                record["service"], record["endpoint"], record["entity_type"], 
                record["entity_value"], status_code, processing_time_ms, record["event_type"]
            )
            print("SERVICE\t{}".format(csv_out))
            
        else:
            # Unrecognized log format
            print("INVALID\t{}".format(line))
            
    except Exception:
        # Catch syntax errors or type casting failures
        print("INVALID\t{}".format(line))