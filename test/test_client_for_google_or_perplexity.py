"""Test client for GodsEye API analysis endpoint."""
import json

import requests

# Your Local Backend
API_URL = "http://127.0.0.1:5000/analyze"

# --- ⚠️ IMPORTANT: PUT A REAL ID FROM YOUR DATABASE HERE ---
REAL_PRODUCT_ID = "02f92e70-7b53-45b6-bdef-7ef36d8fc578" 

def trigger_analysis():
    payload = {
  "product_id": REAL_PRODUCT_ID,
  "engine": "perplexity", 
#   "engine": "google", 
  "debug": True,
}

    print(f"📨 Sending Request for Product: {REAL_PRODUCT_ID}...")
    
    try:
        response = requests.post(API_URL, json=payload)
        
        # Parse JSON
        try:
            data = response.json()
        except:
            print(f"❌ Server returned non-JSON: {response.text}")
            return

        # Handle Logic
        if response.status_code == 200 and data.get('success'):
            print("\n✅ Request Successful!")
            print("-" * 30)
            
            # SCENARIO A: Analysis happened (Data Key Exists)
            if 'data' in data:
                print(f"Score: {data['data']['global_score']}")
                print(f"Narrative: {data['data']['narrative']}")
            
            # SCENARIO B: No Analysis needed (Message Key Exists)
            elif 'message' in data:
                print(f"ℹ️ Status: {data['message']}")
                print("   (No new queries found to analyze)")
            
            print("-" * 30)
        else:
            print("\n⚠️ Analysis Failed.")
            print(f"Status Code: {response.status_code}")
            # Safely get error message even if 'error' key is missing
            print(f"Error Message: {data.get('error', data)}")

    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to localhost:5000. Is the backend running?")

if __name__ == "__main__":
    trigger_analysis()