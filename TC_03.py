#!/usr/bin/env python3
import json
import uuid
import requests
from datetime import datetime, timezone
# Import from nocs_config
from creds import SETTLE_ENDPOINT, BAP_ID, BAP_URI, BPP_ID, BPP_URI, COLLECTOR_APP_ID, RECEIVER_APP_ID

unique_id = str(uuid.uuid4())[:8]
transaction_id = f"tc03-txn-{unique_id}"
message_id = f"tc03-msg-{unique_id}"
current_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

# Test payload - Valid settlement type but missing Authorization header
payload = {
    "context": {
        "domain": "ONDC:NTS10",
        "location": {"country": {"code": "IND"}, "city": {"code": "std:080"}},
        "version": "2.0.0", 
        "action": "settle",
        "bap_id": BAP_ID,
        "bap_uri": BAP_URI,
        "bpp_id": BPP_ID,
        "bpp_uri": BPP_URI,
        "transaction_id": transaction_id,
        "message_id": message_id,
        "timestamp": current_timestamp, 
        "ttl": "P1D"
    },
    "message": {
        "collector_app_id": COLLECTOR_APP_ID,
        "receiver_app_id": RECEIVER_APP_ID,
        "settlement": {
            "type": "NIL"
        }
    }
}

def test_nocs_api():
    print("TC_03: Signature validation - Missing Authorization header")
    
    # Convert payload to minified JSON string
    request_body_raw_text = json.dumps(payload, separators=(',', ':'))
    
    # Prepare headers WITHOUT authorization
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'nocs-user/2.0.0'
        # Missing Authorization and X-Gateway-Authorization headers
    }
    
    # Make the API call
    try:
        response = requests.post(
            SETTLE_ENDPOINT,
            headers=headers,
            data=request_body_raw_text,
            timeout=30
        )

        print(f"Status: {response.status_code} | Txn: {transaction_id} | Msg: {message_id} | timestamp: {payload['context']['timestamp']}")
        print(f"Response: {json.dumps(response.json(), separators=(',', ':'))}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_nocs_api() 