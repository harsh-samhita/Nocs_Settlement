#!/usr/bin/env python3
import json
import requests
import time
import uuid
from datetime import datetime, timezone
from creds import SETTLE_ENDPOINT, get_headers, COLLECTOR_APP_ID, RECEIVER_APP_ID, BAP_ID, BAP_URI, BPP_ID, BPP_URI,PRIVATE_KEY,SUBSCRIBER_ID

unique_id = str(uuid.uuid4())[:8]
transaction_id_1 = f"tc06-txn-{unique_id}-1"
transaction_id_2 = f"tc06-txn-{unique_id}-2"
message_id_1 = f"tc06-msg-{unique_id}-1"
message_id_2 = f"tc06-msg-{unique_id}-2"
settlement_id = f"settlement-tc06-{unique_id}"
current_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def test_nocs_api():
    print("TC_06: Duplicate settlement_id")
    
    # First request
    payload1 = {
        "context": {
            "domain": "ONDC:NTS10",
            "location": {"country": {"code": "IND"}, "city": {"code": "*"}},
            "version": "2.0.0",
            "action": "settle",
            "bap_id": BAP_ID,
            "bap_uri": BAP_URI,
            "bpp_id": BPP_ID,
            "bpp_uri": BPP_URI,
            "transaction_id": transaction_id_1,
            "message_id": message_id_1,
            "timestamp": current_timestamp,
            "ttl": "P1D"
        },
        "message": {
            "collector_app_id": COLLECTOR_APP_ID,
            "receiver_app_id": RECEIVER_APP_ID,
            "settlement": {
                "type": "NP-NP",
                "id": settlement_id,  # SAME settlement_id
                "orders": [
                    {
                        "id": f"order-tc06-{unique_id}-1",
                        "inter_participant": {"amount": {"currency": "INR", "value": "1000.00"}},
                        "collector": {"amount": {"currency": "INR", "value": "50.00"}},
                        "provider": {
                            "id": f"prvdr-tc06-{unique_id}-1",
                            "name": "Test Provider",
                            "bank_details": {"account_no": "1234567890", "ifsc_code": "IFSC0001"},
                            "amount": {"currency": "INR", "value": "800.00"}
                        },
                        "self": {"amount": {"currency": "INR", "value": "200.00"}}
                    }
                ]
            }
        }
    }
    
    request_body = json.dumps(payload1, separators=(',', ':'))
    headers = get_headers(SUBSCRIBER_ID,request_body,PRIVATE_KEY)
    
    try:
        response = requests.post(SETTLE_ENDPOINT, headers=headers, data=request_body, timeout=30)
        print(f"Status: {response.status_code} | Txn: {transaction_id_1} | Msg: {message_id_1} | timestamp: {payload1['context']['timestamp']}")
        print(f"Settlement ID: {settlement_id}")
        print(f"Response: {json.dumps(response.json(), separators=(',', ':'))}")
        
        time.sleep(2)
        print("\n--- Waiting 2 seconds ---\n")
        
        # Second request with SAME settlement_id but different transaction_id and message_id
        payload2 = {
            "context": {
                "domain": "ONDC:NTS10",
                "location": {"country": {"code": "IND"}, "city": {"code": "*"}},
                "version": "2.0.0",
                "action": "settle", 
                "bap_id": BAP_ID,
                "bap_uri": BAP_URI,
                "bpp_id": BPP_ID,
                "bpp_uri": BPP_URI,
                "transaction_id": transaction_id_2,  # DIFFERENT transaction_id
                "message_id": message_id_2,  # DIFFERENT message_id
                "timestamp": current_timestamp,
                "ttl": "P1D"
            },
            "message": {
                "collector_app_id": COLLECTOR_APP_ID,
                "receiver_app_id": RECEIVER_APP_ID,
                "settlement": {
                    "type": "NP-NP",
                    "id": settlement_id,  # SAME settlement_id
                    "orders": [
                        {
                            "id": f"order-tc06-{unique_id}-2",
                            "inter_participant": {"amount": {"currency": "INR", "value": "1000.00"}},
                            "collector": {"amount": {"currency": "INR", "value": "50.00"}},
                            "provider": {
                                "id": f"prvdr-tc06-{unique_id}-2",
                                "name": "Test Provider",
                                "bank_details": {"account_no": "1234567890", "ifsc_code": "IFSC0001"},
                                "amount": {"currency": "INR", "value": "800.00"}
                            },
                            "self": {"amount": {"currency": "INR", "value": "200.00"}}
                        }
                    ]
                }
            }
        }
        
        request_body2 = json.dumps(payload2, separators=(',', ':'))
        headers2 = get_headers(SUBSCRIBER_ID,request_body2,PRIVATE_KEY)
        
        response2 = requests.post(SETTLE_ENDPOINT, headers=headers2, data=request_body2, timeout=30)
        print(f"Status: {response2.status_code} | Txn: {transaction_id_2} | Msg: {message_id_2} | timestamp: {payload2['context']['timestamp']}")
        print(f"Response: {json.dumps(response2.json(), separators=(',', ':'))}")
        
        # Check for expected error
        if response2.status_code == 200:
            print("\n✅ Both requests got ACK (may be processed asynchronously)")
        else:
            print(f"\n❌ Both requests got NACK")
    except Exception as e:
        print(f"TC_06 Error: {e}")
if __name__ == "__main__":
    test_nocs_api() 