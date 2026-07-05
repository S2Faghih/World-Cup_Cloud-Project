#!/usr/bin/env python3
import sys

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    
    # We read the raw output from Jobs 2, 3, and 4 on HDFS.
    # We assign them all the exact same key ("SUMMARY") so they all go to 1 Reducer.
    print("SUMMARY\t{}".format(line))