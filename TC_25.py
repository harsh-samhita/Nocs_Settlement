#!/usr/bin/env python3
import json
import requests
import uuid
from datetime import datetime, timezone
# Import from nocs_config
from creds import get_headers, COLLECTOR_APP_ID, RECEIVER_APP_ID, BAP_ID, BAP_URI, BPP_ID, BPP_URI, REPORT_ENDPOINT,PRIVATE_KEY


def test_report_with_invalid_refs():
    print("TC_25: Report - Business validation (Invalid Reference IDs)")
    print("Expected: ACK, Failed order settlement with error code: 70028")
    
    unique_id = str(uuid.uuid4())[:8]
    report_message_id = f"tc25-report-{unique_id}"
    report_transaction_id = f"tc25-report-txn-{unique_id}"
    current_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
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
            "ref_transaction_id": f"invalid-transaction-id-{unique_id}",
            "ref_message_id": f"invalid-message-id-{unique_id}"
        }
    }
    
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
            print("\n✅ Report request got ACK successful!")
            return True
        else:
            print("\n❌ Report request got NACK!")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_nocs_api():
    report_success = test_report_with_invalid_refs()
    
    if report_success:
        print(f"\n🎉 TC_25 Complete: Report with invalid reference IDs got ACK successful!")
    else:
        print("\n❌ TC_25 Failed: Report request got NACK!")

if __name__ == "__main__":
    test_nocs_api() 
