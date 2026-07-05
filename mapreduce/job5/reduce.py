#!/usr/bin/env python3
import sys
import json

data = {
    "service_stats": [],
    "endpoint_stats": [],
    "team_req": {},
    "match_req": {},
    "stadium_req": {},
    "team_pop": {}
}

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
        
    try:
        # Split out the "SUMMARY" key
        key, val = line.split('\t', 1)
        # val is formatted as: PREFIX\tDATA (e.g., SERVICE_FINAL\tteam-service,100,...)
        prefix, actual_data = val.split('\t', 1)
        parts = actual_data.split(',')
        
        if prefix == "SERVICE_FINAL":
            # svc, t_req, t_success, t_4xx, t_5xx, err_rate, avg_time
            data["service_stats"].append({
                "service": parts[0],
                "reqs": int(parts[1]),
                "err_rate": float(parts[5])
            })
        elif prefix == "ENDPOINT_FINAL":
            # ep, t_req, avg_time
            data["endpoint_stats"].append({
                "endpoint": parts[0],
                "reqs": int(parts[1]),
                "avg_time": float(parts[2])
            })
        elif prefix == "TEAM_REQ":
            # country, team, count
            team = parts[1]
            count = int(parts[2])
            data["team_req"][team] = data["team_req"].get(team, 0) + count
        elif prefix == "MATCH_REQ":
            match = parts[1]
            count = int(parts[2])
            data["match_req"][match] = data["match_req"].get(match, 0) + count
        elif prefix == "STADIUM_REQ":
            stadium = parts[1]
            count = int(parts[2])
            data["stadium_req"][stadium] = data["stadium_req"].get(stadium, 0) + count
        elif prefix == "TEAM_POP":
            # country, team, count
            country = parts[0]
            team = parts[1]
            data["team_pop"][country] = team
    except Exception:
        continue

# 1. Calculate general stats
total_reqs = sum(s["reqs"] for s in data["service_stats"])

most_req_svc = ""
max_svc_req = -1
highest_err_svc = ""
max_err_rate = -1
for s in data["service_stats"]:
    if s["reqs"] > max_svc_req:
        max_svc_req = s["reqs"]
        most_req_svc = s["service"]
    if s["err_rate"] > max_err_rate:
        max_err_rate = s["err_rate"]
        highest_err_svc = s["service"]
        
slowest_ep = ""
max_ep_time = -1
for e in data["endpoint_stats"]:
    if e["avg_time"] > max_ep_time:
        max_ep_time = e["avg_time"]
        slowest_ep = e["endpoint"]

# 2. Helper to find the top entities
def get_top_entities(req_dict, n=1):
    sorted_entities = sorted(req_dict.items(), key=lambda x: x[1], reverse=True)
    if not sorted_entities:
        return "" if n == 1 else []
    if n == 1:
        return sorted_entities[0][0]
    return [x[0] for x in sorted_entities[:n]]

# 3. Calculate Predictions
top_team = get_top_entities(data["team_req"], 1)
top_2_teams = get_top_entities(data["team_req"], 2)
top_match = get_top_entities(data["match_req"], 1)
top_stadium = get_top_entities(data["stadium_req"], 1)

predicted_final = ""
if len(top_2_teams) >= 2:
    predicted_final = "{} vs {}".format(top_2_teams[0], top_2_teams[1])
elif len(top_2_teams) == 1:
    predicted_final = top_2_teams[0]

# Build the final JSON object
summary = {
    "total_requests": total_reqs,
    "most_requested_service": most_req_svc,
    "highest_error_rate_service": highest_err_svc,
    "slowest_endpoint": slowest_ep,
    "most_popular_team_overall": top_team,
    "most_requested_match_day_overall": top_match,
    "most_requested_stadium_overall": top_stadium,
    "popular_team_by_country": data["team_pop"],
    "predicted_champion": top_team,
    "predicted_final": predicted_final,
    "predicted_final_winner": top_team,
    "predicted_final_stadium": top_stadium
}

# Print the JSON payload (Hadoop will save this to part-00000)
print(json.dumps(summary, indent=4))