#!/usr/bin/env python3
import json
import requests
import time
import uuid
from datetime import datetime, timezone
# Import from nocs_config
from creds import SETTLE_ENDPOINT, get_headers, COLLECTOR_APP_ID, RECEIVER_APP_ID, BAP_ID, BAP_URI, BPP_ID, BPP_URI,PRIVATE_KEY,BUYER_KEY

unique_id = str(uuid.uuid4())[:8]
transaction_id_1 = f"tc16-txn-{unique_id}"
transaction_id_2 = f"tc16-txn-{unique_id}-2"
message_id_1 = f"tc16-msg-{unique_id}-1"
message_id_2 = f"tc16-msg-{unique_id}-2"
current_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def test_receiver_first_settlement():
    print("Step 1: Receiver sends valid amount first")
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
                "id": f"settlement-tc16-receiver-{transaction_id_1}",
                "orders": [
                    {
                        "id": f"order-tc16-{transaction_id_1}",
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
                            "id": f"prvdr-tc16-{transaction_id_1}",
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
    
    # Send receiver settlement first
    request_body_raw_text = json.dumps(receiver_payload, separators=(',', ':'))
    headers = get_headers(RECEIVER_APP_ID,request_body_raw_text,BUYER_KEY)
    
    try:
        response = requests.post(
            SETTLE_ENDPOINT,
            headers=headers,
            data=request_body_raw_text,
            timeout=30
        )
        
        print(f"Status: {response.status_code} | Txn: {transaction_id_1} | Msg: {message_id_1} | timestamp: {receiver_payload['context']['timestamp']}")
        print(f"Response: {json.dumps(response.json(), separators=(',', ':'))}")
        
        if response.status_code == 200:
            print("\n✅ Receiver settlement got ACK!")
            return True, transaction_id_1, message_id_2
        else:
            print("\n❌ Receiver settlement got NACK!")
            return False, None, None
            
    except Exception as e:
        print(f"Error: {e}")
        return False, None, None

# def test_collector_no_settlement():
#     print("Second: Collector does NOT send settlement")
#     return True

# def test_receiver_second_settlement(transaction_id, message_id_2):
#     print("Third: Receiver sends second settlement")
#     receiver_payload_2 = {
#         "context": {
#             "domain": "ONDC:NTS10",
#             "location": {"country": {"code": "IND"}, "city": {"code": "*"}},
#             "version": "2.0.0", 
#             "action": "settle",
#             "bap_id": BAP_ID,
#             "bap_uri": BAP_URI,
#             "bpp_id": BPP_ID,
#             "bpp_uri": BPP_URI,
#             "transaction_id": transaction_id,  # Same transaction_id
#             "message_id": message_id_2,  # Different message_id
#             "timestamp": "2025-07-24T08:35:00.800Z", 
#             "ttl": "P1D"
#         },
#         "message": {
#             "collector_app_id": COLLECTOR_APP_ID,
#             "receiver_app_id": RECEIVER_APP_ID,
#             "settlement": {
#                 "type": "NP-NP",
#                 "id": f"settlement-tc16-receiver-2-{transaction_id}",
#                 "orders": [
#                     {
#                         "id": f"order-tc16-{transaction_id}",
#                         "inter_participant": {
#                             "amount": {
#                                 "currency": "INR",
#                                 "value": "1000.00"  # Same amount
#                             }
#                         },
#                         "collector": {
#                             "amount": {
#                                 "currency": "INR",
#                                 "value": "50.00"  # Same amount
#                             }
#                         },
#                         "provider": {
#                             "id": f"prvdr-tc16-{transaction_id}",
#                             "name": "Test Provider",
#                             "bank_details": {
#                                 "account_no": "1234567890",
#                                 "ifsc_code": "IFSC0001"
#                             },
#                             "amount": {
#                                 "currency": "INR",
#                                 "value": "800.00"  # Same amount
#                             }
#                         },
#                         "self": {
#                             "amount": {
#                                 "currency": "INR",
#                                 "value": "200.00"  # Same amount
#                             }
#                         }
#                     }
#                 ]
#             }
#         }
#     }
    
#     # Send receiver settlement second
#     request_body_raw_text = json.dumps(receiver_payload_2, separators=(',', ':'))
#     headers = get_headers(request_body_raw_text)
    
#     try:
#         response = requests.post(
#             SETTLE_ENDPOINT,
#             headers=headers,
#             data=request_body_raw_text,
#             timeout=30
#         )
        
#         print(f"Status: {response.status_code} | Txn: {transaction_id} | Msg: {message_id_2} | timestamp: {receiver_payload_2['context']['timestamp']}")
#         print(f"Response: {json.dumps(response.json(), separators=(',', ':'))}")
        
#         if response.status_code == 200:
#             print("\n✅ Receiver second settlement successful!")
#             return True
#         else:
#             print("\n❌ Receiver second settlement failed!")
#             return False
            
#     except Exception as e:
#         print(f"Error: {e}")
#         return False

def test_nocs_api():
    print("TC_16: 2-way Reconciliation - Receiver First")
    receiver_success, transaction_id_1, message_id_1 = test_receiver_first_settlement()
    
    # if receiver_success:
    #     print("\n--- Waiting 10 seconds ---")
    #     time.sleep(10)
        # collector_simulated = test_collector_no_settlement()
    
        # if collector_simulated:
        #     print("\n--- Waiting 10 seconds ---")
        #     time.sleep(10)
        #     receiver_second_success = test_receiver_second_settlement(transaction_id, message_id_2)
            
    if receiver_success:
        print(f"\n🎉 TC_16 Complete: Test scenario got ACK successful!")
    else:
        print("\n❌ TC_16 Failed: Receiver settlement got NACK!")

if __name__ == "__main__":
    test_nocs_api() 