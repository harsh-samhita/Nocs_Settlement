#!/usr/bin/env python3
import json
import requests
import time
import uuid

# Import from nocs_config
from creds import SETTLE_ENDPOINT, get_headers, COLLECTOR_APP_ID, RECEIVER_APP_ID

def test_collector_settlement():
    """First: Collector sends valid data for LSP receiver"""
    print("=== TC_18: 2-way Reconciliation for LSP receiver (LSP without NOCA account) ===")
    print("Step 1: Collector sends /settle payload with valid data")
    print("Expected: ACK, Successful order settlement with settlement reference number")
    
    # Generate unique IDs for this test run
    unique_id = str(uuid.uuid4())[:8]
    transaction_id = f"tc18-txn-{unique_id}"
    message_id_1 = f"tc18-msg-{unique_id}-1"
    message_id_2 = f"tc18-msg-{unique_id}-2"
    
    # Collector settlement payload - Valid data
    collector_payload = {
        "context": {
            "domain": "ONDC:NTS10",
            "location": {"country": {"code": "IND"}, "city": {"code": "*"}},
            "version": "2.0.0", 
            "action": "settle",
            "bap_id": "staging-smartsell.samhita.org",
            "bap_uri": "https://staging-smartsell.samhita.org/ondc/api/v1",
            "bpp_id": "sa_nocs.nbbl.com",
            "bpp_uri": "https://sa_nocs.nbbl.com/nocs_test",
            "transaction_id": transaction_id,
            "message_id": message_id_1,
            "timestamp": "2025-07-24T08:35:00.800Z", 
            "ttl": "P1D"
        },
        "message": {
            "collector_app_id": COLLECTOR_APP_ID,
            "receiver_app_id": RECEIVER_APP_ID,
            "settlement": {
                "type": "NP-NP",
                "id": f"settlement-tc18-{unique_id}",
                "orders": [
                    {
                        "id": f"order-tc18-{unique_id}",
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
                            "id": f"prvdr-tc18-{unique_id}",
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
    headers = get_headers(request_body_raw_text)
    
    try:
        response = requests.post(
            SETTLE_ENDPOINT,
            headers=headers,
            data=request_body_raw_text,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✅ Collector settlement successful!")
            return True, transaction_id, message_id_2
        else:
            print("\n❌ Collector settlement failed!")
            return False, None, None
            
    except Exception as e:
        print(f"Error: {e}")
        return False, None, None

def test_receiver_settlement(transaction_id, message_id_2):
    """Second: Receiver (LSP) sends valid data"""
    print("\nStep 2: Receiver (LSP) sends /settle payload with valid data")
    print("Expected: ACK, Successful order settlement with settlement reference number")
    
    # Receiver settlement payload - Valid data (matching amounts)
    receiver_payload = {
        "context": {
            "domain": "ONDC:NTS10",
            "location": {"country": {"code": "IND"}, "city": {"code": "*"}},
            "version": "2.0.0", 
            "action": "settle",
            "bap_id": "staging-smartsell.samhita.org",  # Same BAP for signature
            "bap_uri": "https://staging-smartsell.samhita.org/ondc/api/v1",
            "bpp_id": "sa_nocs.nbbl.com",
            "bpp_uri": "https://sa_nocs.nbbl.com/nocs_test",
            "transaction_id": transaction_id,  # Same transaction_id
            "message_id": message_id_2,  # Different message_id
            "timestamp": "2025-07-24T08:35:00.800Z", 
            "ttl": "P1D"
        },
        "message": {
            "collector_app_id": COLLECTOR_APP_ID,
            "receiver_app_id": RECEIVER_APP_ID,
            "settlement": {
                "type": "NP-NP",
                "id": f"settlement-tc18-receiver-{transaction_id}",
                "orders": [
                    {
                        "id": f"order-tc18-{transaction_id}",
                        "inter_participant": {
                            "amount": {
                                "currency": "INR",
                                "value": "1000.00"  # Exact matching amount
                            }
                        },
                        "collector": {
                            "amount": {
                                "currency": "INR",
                                "value": "50.00"  # Exact matching amount
                            }
                        },
                        "provider": {
                            "id": f"prvdr-tc18-{transaction_id}",
                            "name": "Test Provider",
                            "bank_details": {
                                "account_no": "1234567890",
                                "ifsc_code": "IFSC0001"
                            },
                            "amount": {
                                "currency": "INR",
                                "value": "800.00"  # Exact matching amount
                            }
                        },
                        "self": {
                            "amount": {
                                "currency": "INR",
                                "value": "200.00"  # Exact matching amount
                            }
                        }
                    }
                ]
            }
        }
    }
    
    # Send receiver settlement
    request_body_raw_text = json.dumps(receiver_payload, separators=(',', ':'))
    headers = get_headers(request_body_raw_text)
    
    try:
        response = requests.post(
            SETTLE_ENDPOINT,
            headers=headers,
            data=request_body_raw_text,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✅ Receiver (LSP) settlement successful!")
            return True
        else:
            print("\n❌ Receiver (LSP) settlement failed!")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_nocs_api():
    """Run the complete 2-way reconciliation test with LSP receiver"""
    # Step 1: Collector settlement
    collector_success, transaction_id, message_id_2 = test_collector_settlement()
    
    if collector_success:
        # Wait a moment between requests
        print("\n--- Waiting 2 seconds ---")
        time.sleep(2)
        
        # Step 2: Receiver settlement
        receiver_success = test_receiver_settlement(transaction_id, message_id_2)
        
        if receiver_success:
            print(f"\n🎉 TC_18 Complete: Both settlements successful!")
            print(f"Transaction ID: {transaction_id}")
            print("LSP receiver test completed!")
            print("Check database for settlement reference number!")
        else:
            print("\n❌ TC_18 Failed: Receiver settlement failed!")
    else:
        print("\n❌ TC_18 Failed: Collector settlement failed!")

if __name__ == "__main__":
    test_nocs_api() 