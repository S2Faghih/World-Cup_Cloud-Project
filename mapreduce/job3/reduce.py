#!/usr/bin/env python3
import sys

current_key = None
current_count = 0

def emit(key_str, count):
    # key_str is now formatted as "service|country|entity_val"
    parts = key_str.split('|')
    if len(parts) == 3:
        service, country, entity_val = parts
        
        # Route to the appropriate final file prefix based on the service
        if service == "team-service":
            print("TEAM_REQ\t{},{},{}".format(country, entity_val, count))
        elif service == "match-service":
            print("MATCH_REQ\t{},{},{}".format(country, entity_val, count))
        elif service == "stadium-service":
            print("STADIUM_REQ\t{},{},{}".format(country, entity_val, count))

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
        
    try:
        # Split by the tab to separate our compound key from the count (1)
        key_str, count_str = line.split('\t', 1)
        count = int(count_str)
    except ValueError:
        continue

    if current_key == key_str:
        current_count += count
    else:
        if current_key:
            emit(current_key, current_count)
        
        current_key = key_str
        current_count = count

# Emit the final key group
if current_key:
    emit(current_key, current_count)