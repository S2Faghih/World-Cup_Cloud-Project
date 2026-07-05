#!/usr/bin/env python3
import sys

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    parts = line.split(',')
    
    if len(parts) != 10:
        continue
    
    country = parts[2]
    service = parts[3]
    entity_val = parts[6]
    
    print("{}|{}|{}\t1".format(service, country, entity_val))