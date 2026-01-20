#!/usr/bin/env python3
import json
import requests
import uuid
from datetime import datetime, timezone
# Import from nocs_config
from creds import SETTLE_ENDPOINT, get_headers, COLLECTOR_APP_ID, RECEIVER_APP_ID, BAP_ID, BAP_URI, BPP_ID, BPP_URI,PRIVATE_KEY

unique_id = str(uuid.uuid4())[:8]
transaction_id = f"tc22-txn-{unique_id}"
message_id = f"tc22-msg-{unique_id}"
current_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def test_nocs_api():
    print("TC_22: MISC type with self or provider details")
    print("Expected: ACK, Successful order settlement with settlement reference number")
    
    # MISC settlement payload with self and provider details
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
            "settlement": {
                "type": "MISC",
                "id": f"settlement-tc22-{unique_id}",
                "orders": [
                    {
                        "self": {
                            "amount": {
                                "currency": "INR",
                                "value": "200.00"
                            }
                        },
                        "provider": {
                            "id": f"prvdr-tc22-{unique_id}",
                            "name": "Test Provider",
                            "bank_details": {
                                "account_no": "1234567890",
                                "ifsc_code": "IFSC0001"
                            },
                            "amount": {
                                "currency": "INR",
                                "value": "200.00"
                            }
                        }
                    }
                ]
            }
        }
    }
    
    # Send MISC settlement
    request_body_raw_text = json.dumps(payload, separators=(',', ':'))
    headers = get_headers(BAP_ID,request_body_raw_text,PRIVATE_KEY)
    
    try:
        response = requests.post(
            SETTLE_ENDPOINT,
            headers=headers,
            data=request_body_raw_text,
            timeout=30
        )
        
        print(f"Status: {response.status_code} | Txn: {transaction_id} | Msg: {message_id} | timestamp: {payload['context']['timestamp']}")
        print(f"Response: {json.dumps(response.json(), separators=(',', ':'))}")
        
        if response.status_code == 200:
            print(f"\n✅ MISC settlement got ACK successful!")  
        else:
            print("\n❌ MISC settlement got NACK!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_nocs_api() 