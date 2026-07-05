#!/usr/bin/env python3
import sys

current_key = None
max_entity = None
max_count = -1

def emit(key_str, entity, count):
    parts = key_str.split('|')
    if len(parts) == 2:
        prefix, country = parts
        
        if prefix == "TEAM_REQ":
            print("TEAM_POP\t{},{},{}".format(country, entity, count))
        elif prefix == "MATCH_REQ":
            print("MATCH_POP\t{},{},{}".format(country, entity, count))
        elif prefix == "STADIUM_REQ":
            print("STADIUM_POP\t{},{},{}".format(country, entity, count))

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    
    try:
        key_str, val_str = line.split('\t', 1)
        entity, count_str = val_str.split('|')
        count = int(count_str)
    except ValueError:
        continue

    if current_key == key_str:
        if count > max_count:
            max_count = count
            max_entity = entity
    else:
        # Key changed. Emit the winner for the previous country
        if current_key:
            emit(current_key, max_entity, max_count)
        
        # Reset trackers for the new country
        current_key = key_str
        max_count = count
        max_entity = entity

if current_key:
    emit(current_key, max_entity, max_count)