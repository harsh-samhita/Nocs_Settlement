#!/usr/bin/env python3
import json
import requests
import time
import uuid
from datetime import datetime, timezone
# Import from nocs_config
from creds import SETTLE_ENDPOINT, get_headers, COLLECTOR_APP_ID, RECEIVER_APP_ID, BAP_ID, BAP_URI, BPP_ID, BPP_URI,PRIVATE_KEY,BUYER_KEY

unique_id = str(uuid.uuid4())[:8]
transaction_id_1 = f"tc13-txn-{unique_id}"
transaction_id_2 = f"tc13-txn-{unique_id}-2"
message_id_1 = f"tc13-msg-{unique_id}-1"
message_id_2 = f"tc13-msg-{unique_id}-2"
current_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def test_collector_settlement():
    print("TC_13: 2-way Reconciliation - Receiver NIL Settle")
    print("Step 1: Collector sends valid data")
    
    collector_payload = {
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
                "id": f"settlement-tc13-{unique_id}",
                "orders": [
                    {
                        "id": f"order-tc13-{unique_id}",
                        "inter_participant": {
                            "amount": {
                                "currency": "INR",
                                "value": "1000.00"
                            }
                        },
                        "collector": {
                            "amount": {
                                "currency": "INR",
                                "value": "50.00"
                            }
                        },
                        "provider": {
                            "id": f"prvdr-tc13-{unique_id}",
                            "name": "Test Provider",
                            "bank_details": {
                                "account_no": "1234567890",
                                "ifsc_code": "IFSC0001"
                            },
                            "amount": {
                                "currency": "INR",
                                "value": "800.00"
                            }
                        },
                        "self": {
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
    
    # Send collector settlement
    request_body_raw_text = json.dumps(collector_payload, separators=(',', ':'))
    headers = get_headers(BAP_ID,request_body_raw_text,PRIVATE_KEY)
    
    try:
        response = requests.post(
            SETTLE_ENDPOINT,
            headers=headers,
            data=request_body_raw_text,
            timeout=30
        )
        
        print(f"Status: {response.status_code} | Txn: {transaction_id_1} | Msg: {message_id_1} | timestamp: {collector_payload['context']['timestamp']}")
        print(f"Response: {json.dumps(response.json(), separators=(',', ':'))}")
        
        if response.status_code == 200:
            print("\n✅ Collector settlement got ACK!")
            return True, transaction_id_1, message_id_2
        else:
            print("\n❌ Collector settlement got NACK!")
            return False, None, None
            
    except Exception as e:
        print(f"Error: {e}")
        return False, None, None

def test_receiver_settlement(transaction_id_2, message_id_2):
    print("Second: Receiver sends NIL settlement type")
    
    receiver_payload = {
        "context": {
            "domain": "ONDC:NTS10",
            "location": {"country": {"code": "IND"}, "city": {"code": "*"}},
            "version": "2.0.0", 
            "action": "settle",
            "bap_id": RECEIVER_APP_ID,
            "bap_uri": BAP_URI,
            "bpp_id": BPP_ID,
            "bpp_uri": BPP_URI,
            "transaction_id": transaction_id_2,  # Different transaction_id
            "message_id": message_id_2,  # Different message_id
            "timestamp": current_timestamp, 
            "ttl": "P1D"
        },
        "message": {
            "settlement": {
                "type": "NIL"  # NIL settlement type
            }
        }
    }
    
    # Send receiver settlement
    request_body_raw_text = json.dumps(receiver_payload, separators=(',', ':'))
    headers = get_headers(RECEIVER_APP_ID,request_body_raw_text,BUYER_KEY)
    
    try:
        response = requests.post(
            SETTLE_ENDPOINT,
            headers=headers,
            data=request_body_raw_text,
            timeout=30
        )
        
        print(f"Status: {response.status_code} | Txn: {transaction_id_2} | Msg: {message_id_2} | timestamp: {receiver_payload['context']['timestamp']}")
        print(f"Response: {json.dumps(response.json(), separators=(',', ':'))}")
        
        if response.status_code == 200:
            print("\n✅ Receiver NIL settlement got ACK!")
            return True
        else:
            print("\n❌ Receiver NIL settlement got NACK!")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_nocs_api():
    collector_success, transaction_id_1, message_id_1 = test_collector_settlement()
    
    if collector_success:
        print("\n--- Waiting 10 seconds ---")
        time.sleep(10)
        
        receiver_success = test_receiver_settlement(transaction_id_2, message_id_2)
        
        if receiver_success:
            print(f"\n🎉 TC_13 Complete: Both settlements got ACK successful!")
        else:
            print("\n❌ TC_13 Failed: Receiver settlement got NACK!")
    else:
        print("\n❌ TC_13 Failed: Collector settlement got NACK!")

if __name__ == "__main__":
    test_nocs_api() 