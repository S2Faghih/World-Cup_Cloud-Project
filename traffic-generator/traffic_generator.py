import requests
import random
import uuid
import time
import argparse

# Simulate different countries for X-Client-Country header
COUNTRIES = ["Iran", "Germany", "Argentina", "Brazil", "USA", "France", "Japan", "Qatar"]

# Scenarios to simulate normal traffic, slow responses, and 500 errors
SCENARIOS = ["normal", "normal", "normal", "normal", "normal", "slow", "server_error"]

# Data pools
TEAMS = ["Argentina", "Brazil", "France", "Iran", "Germany", "Atlantis"] 
MATCH_DATES = ["2026-06-12", "2026-06-25", "2026-07-04", "2026-13-99", ""] 
STADIUMS = ["New York New Jersey Stadium", "Dallas Stadium", "Lusail Stadium", "Unknown Stadium"] 

def generate_request(base_url):
    """Generates a single randomized request to the Nginx Gateway."""
    country = random.choice(COUNTRIES)
    scenario = random.choice(SCENARIOS)
    req_id = f"req_{uuid.uuid4().hex[:8]}"

    headers = {
        "X-Request-ID": req_id,
        "X-Client-Country": country,
        "X-Scenario": scenario
    }

    target = random.choice(["team", "match", "stadium"])
    
    if random.random() < 0.2:
        team_query = "Argentina"
    else:
        team_query = random.choice(TEAMS)

    if target == "team":
        url = f"{base_url}/api/teams?name={team_query}"
    elif target == "match":
        date = random.choice(MATCH_DATES)
        url = f"{base_url}/api/matches?date={date}"
    else:
        stadium = random.choice(STADIUMS)
        url = f"{base_url}/api/stadiums?name={stadium}"

    try:
        response = requests.get(url, headers=headers, timeout=5)
        print(f"[{req_id}] {country} -> {url} | Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[{req_id}] Failed to connect: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate World Cup API traffic.")
    parser.add_argument("--count", type=int, default=1500, help="Number of requests to generate")
    parser.add_argument("--url", type=str, default="http://localhost", help="Base URL of the Nginx Gateway")
    args = parser.parse_args()
    
    print(f"Starting Traffic Generator: Sending {args.count} requests to {args.url}...")
    
    for i in range(args.count):
        generate_request(args.url)
        time.sleep(0.01)
        
    print("Traffic generation completed successfully!")