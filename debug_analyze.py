import requests
import json

url = "http://127.0.0.1:8001/analyze"
payload = {"repo_url": "https://github.com/Devika-Sajeesh/learnify-backend"}
headers = {"Content-Type": "application/json"}

try:
    print(f"Sending request to {url}...")
    response = requests.post(url, json=payload, headers=headers, timeout=60)
    print(f"Status Code: {response.status_code}")
    try:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
    except:
        print("Response Text:")
        print(response.text)
except Exception as e:
    print(f"Request failed: {e}")
