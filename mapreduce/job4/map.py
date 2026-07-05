#!/usr/bin/env python3
import sys

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    
    try:
        # We read the raw output from Job 3 on HDFS: PREFIX\tcountry,entity,count
        prefix, data = line.split('\t', 1)
        country, entity, count = data.split(',')
        
        # Composite Key: PREFIX|country
        # Value: entity|count
        print("{}|{}\t{}|{}".format(prefix, country, entity, count))
    except ValueError:
        continue