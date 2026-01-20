#!/usr/bin/env python3
import json
import requests
import time
import uuid
from datetime import datetime, timezone
# Import from creds
from creds import SETTLE_ENDPOINT, get_headers, COLLECTOR_APP_ID, RECEIVER_APP_ID, BAP_ID, BAP_URI, BPP_ID, BPP_URI,PRIVATE_KEY,BUYER_KEY

unique_id = str(uuid.uuid4())[:8]
transaction_id = f"tc04-txn-{unique_id}"
message_id_1 = f"tc04-msg-{unique_id}-1"
message_id_2 = f"tc04-msg-{unique_id}-2"
current_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def test_first_settlement():
    """First: Send settlement with original collector-receiver"""
    print("TC_04: Business validation - Duplicate transaction_id (Same collector-receiver)")
    print("--- First Request (Original settlement) ---")
    
    # First settlement payload
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
            "transaction_id": transaction_id,
            "message_id": message_id_1,
            "timestamp": current_timestamp, 
            "ttl": "P1D"
        },
        "message": {
            "collector_app_id": COLLECTOR_APP_ID,
            "receiver_app_id": RECEIVER_APP_ID,
            "settlement": {
                "type": "NP-NP",
                "id": f"settlement-tc04-{unique_id}",
                "orders": [
                    {
                        "id": f"order-tc04-{unique_id}",
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
                            "id": f"prvdr-tc04-{unique_id}",
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
    
    # print(f"Payload1: {json.dumps(payload1, separators=(',', ':'))}")
    # Send first settlement
    request_body_raw_text = json.dumps(payload1, separators=(',', ':'))
    headers = get_headers(BAP_ID,request_body_raw_text,PRIVATE_KEY)
    
    try:
        response = requests.post(
            SETTLE_ENDPOINT,
            headers=headers,
            data=request_body_raw_text,
            timeout=30
        )
        
        print(f"Status: {response.status_code} | Txn: {transaction_id} | Msg: {message_id_1} | timestamp: {payload1['context']['timestamp']}")
        print(f"Response: {json.dumps(response.json(), separators=(',', ':'))}")
        
        if response.status_code == 200:
            print("\n✅ First settlement sent successfully!")
            return True, transaction_id
        else:
            print("\n❌ First settlement failed!")
            return False, None
            
    except Exception as e:
        print(f"Error: {e}")
        return False, None

def test_second_settlement(transaction_id,message_id_2):
    """Second: Send settlement with SAME collector-receiver, SAME transaction_id"""
    print("\n--- Second Request (Same collector-receiver, same transaction_id) ---")
    
    # Second settlement payload - SAME collector/receiver, SAME transaction_id
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
            "transaction_id": transaction_id,  # SAME transaction_id
            "message_id": message_id_2,
            "timestamp": current_timestamp, 
            "ttl": "P1D"
        },
        "message": {
            "collector_app_id": RECEIVER_APP_ID,
            "receiver_app_id": COLLECTOR_APP_ID,
            "settlement": {
                "type": "NP-NP",
                "id": f"settlement-tc04-duplicate-{unique_id}",
                "orders": [
                    {
                        "id": f"order-tc04-duplicate-{unique_id}",
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
                            "id": f"prvdr-tc04-duplicate-{unique_id}",
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
    # print(f"Payload2: {json.dumps(payload2, separators=(',', ':'))}")
    # Send second settlement
    request_body_raw_text = json.dumps(payload2, separators=(',', ':'))
    headers = get_headers(BAP_ID,request_body_raw_text,PRIVATE_KEY)
    
    try:
        response = requests.post(
            SETTLE_ENDPOINT,
            headers=headers,
            data=request_body_raw_text,
            timeout=30
        )
        
        print(f"Status: {response.status_code} | Txn: {transaction_id} | Msg: {message_id_2} | timestamp: {payload2['context']['timestamp']}")
        print(f"Response: {json.dumps(response.json(), separators=(',', ':'))}")
        
        if response.status_code == 200:
            print("\n✅ Second settlement sent successfully!")
            return True
        else:
            print("\n❌ Second settlement failed!")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_nocs_api():
    """Run the complete duplicate transaction_id test"""
    # Step 1: First settlement
    first_success, transaction_id = test_first_settlement()
    
    if first_success:
        # Wait a moment between requests
        print("\n--- Waiting 2 seconds ---")
        time.sleep(2)
        
        # Step 2: Second settlement with SAME collector/receiver
        second_success = test_second_settlement(transaction_id,message_id_2)
        
        if second_success:
            print(f"\n🎉 TC_04 Complete: Duplicate transaction_id test completed!")
        else:
            print("\n❌ TC_04 Failed: Second settlement failed!")
    else:
        print("\n❌ TC_04 Failed: First settlement failed!")

if __name__ == "__main__":
    test_nocs_api() 