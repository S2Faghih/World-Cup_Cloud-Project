"""
Traffic Generator for Cloud Final Project (Phase 1)
Simulates user traffic hitting the Nginx API Gateway.
"""
import requests
import random
import uuid
import time

# Nginx is listening on port 80 locally
BASE_URL = "http://localhost"

# Simulate different countries for X-Client-Country header
COUNTRIES = ["Iran", "Germany", "Argentina", "Brazil", "USA", "France", "Japan", "Qatar"]

# Scenarios to simulate normal traffic, slow responses, and 500 errors
# We keep "normal" more frequent to reflect realistic traffic
SCENARIOS = ["normal", "normal", "normal", "normal", "normal", "slow", "server_error"]

# Data pools (includes both valid and invalid entries to trigger 404/400 errors)
TEAMS = ["Argentina", "Brazil", "France", "Iran", "Germany", "Atlantis"] # Atlantis will cause 404
MATCH_DATES = ["2026-06-12", "2026-06-25", "2026-07-04", "2026-13-99", ""] # Invalid dates for 400/404
STADIUMS = ["New York New Jersey Stadium", "Dallas Stadium", "Lusail Stadium", "Unknown Stadium"] # Lusail is 2022 -> 404

def generate_request():
    """Generates a single randomized request to the Nginx Gateway."""
    # 1. Generate Headers
    country = random.choice(COUNTRIES)
    scenario = random.choice(SCENARIOS)
    
    # Generate a unique request ID (e.g., req_a1b2c3d4)
    req_id = f"req_{uuid.uuid4().hex[:8]}"

    headers = {
        "X-Request-ID": req_id,
        "X-Client-Country": country,
        "X-Scenario": scenario
    }

    # 2. Choose target service randomly
    target = random.choice(["team", "match", "stadium"])
    
    # 3. Create unbalanced traffic (e.g., Argentina is very popular)
    if random.random() < 0.2:
        team_query = "Argentina"
    else:
        team_query = random.choice(TEAMS)

    # 4. Build URL
    if target == "team":
        url = f"{BASE_URL}/api/teams?name={team_query}"
    elif target == "match":
        date = random.choice(MATCH_DATES)
        url = f"{BASE_URL}/api/matches?date={date}"
    else:
        stadium = random.choice(STADIUMS)
        url = f"{BASE_URL}/api/stadiums?name={stadium}"

    # 5. Send Request
    try:
        response = requests.get(url, headers=headers, timeout=5)
        print(f"[{req_id}] {country} -> {url} | Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[{req_id}] Failed to connect: {e}")

if __name__ == "__main__":
    # Number of requests to generate. Project asks for enough volume to make logs meaningful.
    TOTAL_REQUESTS = 1500
    
    print(f"Starting Traffic Generator: Sending {TOTAL_REQUESTS} requests to Nginx...")
    
    for i in range(TOTAL_REQUESTS):
        generate_request()
        # Small delay to prevent overwhelming the local machine completely
        time.sleep(0.01)
        
    print("Traffic generation completed successfully!")