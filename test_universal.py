import requests
import json

# Tumhara local API endpoint
URL = "http://localhost:8000/api/universal-webhook"

# Ek messy, unstructured Zoom Call Transcript
fake_payload = {
    "source_name": "Zoom Sales Call",
    "raw_data": "Uh, yeah, so during the demo with Microsoft, we were trying to export the Q3 report, and the whole system just completely froze. John was pretty angry because it made us look bad. I think it's related to the new PDF rendering update we pushed last night. Can engineering look into this? It's a massive blocker for our Enterprise clients."
}

print(f"🚀 Sending messy data from [{fake_payload['source_name']}] to AgentOS...")

# Sending the POST request
response = requests.post(URL, json=fake_payload)

print(f"✅ Backend Reply: {json.dumps(response.json(), indent=2)}")
print("⏳ Now check your Next.js Dashboard in 2-3 seconds!")