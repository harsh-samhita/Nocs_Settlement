#!/usr/bin/env python3
import json
import requests
import uuid
from datetime import datetime, timezone
from creds import SETTLE_ENDPOINT, get_headers, COLLECTOR_APP_ID, RECEIVER_APP_ID, BAP_ID, BAP_URI, BPP_ID, BPP_URI,PRIVATE_KEY,SUBSCRIBER_ID

unique_id = str(uuid.uuid4())[:8]
transaction_id = f"tc07-txn-{unique_id}"
message_id = f"tc07-msg-{unique_id}"
duplicate_order_id = f"order-tc07-{unique_id}"  # SAME order ID for both orders
current_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def test_nocs_api():
    print("TC_07: Duplicate orderId within same payload")
    
    # Single request with duplicate orderId within the same payload
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
            "settlement": {
                "type": "NP-NP",
                "id": f"settlement-tc07-{unique_id}",
                "orders": [
                    {
                        "id": duplicate_order_id,  # FIRST order with this ID
                        "inter_participant": {"amount": {"currency": "INR", "value": "1000.00"}},
                        "collector": {"amount": {"currency": "INR", "value": "50.00"}},
                        "provider": {
                            "id": f"prvdr-tc07-{unique_id}-1",
                            "name": "Test Provider 1",
                            "bank_details": {"account_no": "1234567890", "ifsc_code": "IFSC0001"},
                            "amount": {"currency": "INR", "value": "800.00"}
                        },
                        "self": {"amount": {"currency": "INR", "value": "200.00"}}
                    },
                    {
                        "id": duplicate_order_id,  # SECOND order with SAME ID (DUPLICATE)
                        "inter_participant": {"amount": {"currency": "INR", "value": "500.00"}},
                        "collector": {"amount": {"currency": "INR", "value": "25.00"}},
                        "provider": {
                            "id": f"prvdr-tc07-{unique_id}-2",
                            "name": "Test Provider 2",
                            "bank_details": {"account_no": "0987654321", "ifsc_code": "IFSC0002"},
                            "amount": {"currency": "INR", "value": "400.00"}
                        },
                        "self": {"amount": {"currency": "INR", "value": "100.00"}}
                    }
                ]
            }
        }
    }
    
    request_body = json.dumps(payload, separators=(',', ':'))
    headers = get_headers(SUBSCRIBER_ID,request_body,PRIVATE_KEY)
    
    try:
        response = requests.post(SETTLE_ENDPOINT, headers=headers, data=request_body, timeout=30)
        print(f"Status: {response.status_code} | Txn: {transaction_id} | Msg: {message_id} | timestamp: {payload['context']['timestamp']}")
        print(f"Duplicate Order ID: {duplicate_order_id}")
        print(f"Response: {json.dumps(response.json(), separators=(',', ':'))}")
        
        # Check for expected behavior
        if response.status_code == 200:
            print("\n✅ Both requests got ACK (may be processed asynchronously)")
        else:
            print("\n❌ Got NACK as expected")
    except Exception as e:
        print(f"TC_07 Error: {e}")

if __name__ == "__main__":
    test_nocs_api() 