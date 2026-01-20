#!/usr/bin/env python3
import json
import requests
import uuid

# Import from nocs_config
from creds import SETTLE_ENDPOINT, get_headers, COLLECTOR_APP_ID, RECEIVER_APP_ID

def test_nocs_api():
    """Test the NOCS API with MISC type and self/provider details for ISN or LSP"""
    print("=== TC_23: MISC type with self or provider details ISN or LSP ===")
    print("Expected: ACK, Failed order settlement with error code: 70010")
    
    # Generate unique IDs for this test run
    unique_id = str(uuid.uuid4())[:8]
    transaction_id = f"tc23-txn-{unique_id}"
    message_id = f"tc23-msg-{unique_id}"
    
    # MISC settlement payload with self and provider details (ISN/LSP scenario)
    payload = {
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
            "message_id": message_id,
            "timestamp": "2025-07-24T08:35:00.800Z", 
            "ttl": "P1D"
        },
        "message": {
            "collector_app_id": COLLECTOR_APP_ID,  # Adding collector_app_id for ISN/LSP
            "receiver_app_id": RECEIVER_APP_ID,   # Adding receiver_app_id for ISN/LSP
            "settlement": {
                "type": "MISC",
                "id": f"settlement-tc23-{unique_id}",
                "orders": [
                    {
                        "id": f"order-tc23-{unique_id}",
                        "self": {
                            "amount": {
                                "currency": "INR",
                                "value": "200.00"
                            }
                        },
                        "provider": {
                            "id": f"prvdr-tc23-{unique_id}",
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
            print(f"\n✅ MISC settlement successful!")
            print(f"Transaction ID: {transaction_id}")
            print("MISC type with self/provider details ISN/LSP test completed!")
            print("Check database for error code 70010!")
        else:
            print("\n❌ MISC settlement failed!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_nocs_api() 