#!/usr/bin/env python3
import json
import requests
import uuid
from datetime import datetime, timezone
# Import from nocs_config
from creds import SETTLE_ENDPOINT, get_headers, COLLECTOR_APP_ID, RECEIVER_APP_ID, BAP_ID, BAP_URI, BPP_ID, BPP_URI, REPORT_ENDPOINT,PRIVATE_KEY


def test_report_with_valid_refs(transaction_id, message_id):
    print("\nStep 2: Send /report payload with valid ref_transaction_id and ref_message_id")
    print("Expected: ACK, Corresponding status of the /settle transaction will be sent in OnReport")
    unique_id = str(uuid.uuid4())[:8]
    report_transaction_id = f"tc24-report-txn-{unique_id}"
    report_message_id = f"tc24-report-{unique_id}"

    # Generate current timestamp in ISO 8601 format with exactly 3 decimal places (milliseconds)
    current_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    print(f"Current Timestamp: {current_timestamp}")
    
    report_payload = {
        "context": {
            "domain": "ONDC:NTS10",
            "location": {"country": {"code": "IND"}, "city": {"code": "*"}},
            "version": "2.0.0", 
            "action": "report",
            "bap_id": BAP_ID,
            "bap_uri": BAP_URI,
            "bpp_id": BPP_ID,
            "bpp_uri": BPP_URI,
            "transaction_id": report_transaction_id,
            "message_id": report_message_id,
            "timestamp": current_timestamp, 
            "ttl": "P1D"
        },
        "message": {
            "ref_transaction_id": transaction_id,  # Valid reference from previous settle
            "ref_message_id": message_id           # Valid reference from previous settle
        }
    }

    # Send report request
    request_body_raw_text = json.dumps(report_payload, separators=(',', ':'))
    headers = get_headers(BAP_ID,request_body_raw_text,PRIVATE_KEY)
    
    try:
        response = requests.post(
            REPORT_ENDPOINT,
            headers=headers,
            data=request_body_raw_text,
            timeout=30
        )
        
        print(f"Report Status: {response.status_code} | Txn: {report_transaction_id} | Msg: {report_message_id} | timestamp: {report_payload['context']['timestamp']}")
        print(f"Report Response: {json.dumps(response.json(), separators=(',', ':'))}")
        
        if response.status_code == 200:
            print("\n✅ Report got ACK successful!")
            return True
        else:
            print("\n❌ Report got NACK!")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_nocs_api():
    
    # Send report with valid reference IDs
    report_success = test_report_with_valid_refs(
        transaction_id = 'tc04-txn-f212ef6b', #'Valid reference from previous settle transaction here', 
        message_id='tc04-msg-f212ef6b-1' #'Valid reference from previous settle message here'
    )
    
    if report_success:
        print(f"\n🎉 TC_24 Complete: Report with valid reference IDs got ACK successful!")
    else:
        print("\n❌ TC_24 Failed: Report got NACK!")

if __name__ == "__main__":
    test_nocs_api() 