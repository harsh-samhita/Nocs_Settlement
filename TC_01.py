#!/usr/bin/env python3
import json
import requests
import uuid
from datetime import datetime, timezone
from creds import SETTLE_ENDPOINT, get_headers, COLLECTOR_APP_ID, RECEIVER_APP_ID, BAP_ID, BAP_URI, BPP_ID, BPP_URI,PRIVATE_KEY,SUBSCRIBER_ID

def test_nocs_api():
    print("TC_01: Missing settlement type")
    unique_id = str(uuid.uuid4())[:8]
    transaction_id = f"tc01-txn-{unique_id}"
    message_id = f"tc01-msg-{unique_id}"
    current_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    
    payload = {
        "context": {
            "domain": "ONDC:NTS10",
            "location": {"country": {"code": "IND"}, "city": {"code": "*"}},
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
            "settlement": {}  # Missing settlement type - should result in error code 70002
        }
    }
    
    request_body = json.dumps(payload, separators=(',', ':'))
    headers = get_headers(SUBSCRIBER_ID,request_body,PRIVATE_KEY)
    
    try:
        response = requests.post(SETTLE_ENDPOINT, headers=headers, data=request_body, timeout=30)
        print(f"Status: {response.status_code} | Txn: {transaction_id} | Msg: {message_id} | timestamp: {payload['context']['timestamp']}")
        print(f"Response: {json.dumps(response.json(), separators=(',', ':'))}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_nocs_api() 