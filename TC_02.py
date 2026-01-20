#!/usr/bin/env python3
import json
import uuid
import requests
import base64
import datetime
import nacl.encoding
import nacl.hash
from nacl.bindings import crypto_sign_ed25519_sk_to_seed
from nacl.signing import SigningKey
from datetime import datetime, timezone, timedelta
# Import from nocs_config
from creds import SETTLE_ENDPOINT, SUBSCRIBER_ID, UNIQUE_KEY_ID, PRIVATE_KEY, BAP_ID, BAP_URI, BPP_ID, BPP_URI, COLLECTOR_APP_ID, RECEIVER_APP_ID

unique_id = str(uuid.uuid4())[:8]
transaction_id = f"tc02-txn-{unique_id}"
message_id = f"tc02-msg-{unique_id}"
current_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

# Test payload - Valid settlement type but invalid bap id in header
payload = {
    "context": {
        "domain": "ONDC:NTS10",
        "location": {"country": {"code": "IND"}, "city": {"code": "std:080"}},
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
            "type": "NIL"
        }
    }
}

def create_authorisation_header_with_invalid_bap(request_body):
    """Create authorization header with invalid bap_id"""
    created = int(datetime.now().timestamp())
    expires = int((datetime.now() + timedelta(hours=1)).timestamp())
    
    # Hash the message
    HASHER = nacl.hash.blake2b
    digest = HASHER(bytes(request_body, 'utf-8'), digest_size=64, encoder=nacl.encoding.Base64Encoder)
    digest_str = digest.decode("utf-8")
    
    # Create signing string
    signing_string = f"""(created): {created}
                        (expires): {expires}
                        digest: BLAKE-512={digest_str}"""
    
    # Sign the message
    private_key64 = base64.b64decode(PRIVATE_KEY)
    seed = crypto_sign_ed25519_sk_to_seed(private_key64)
    signer = SigningKey(seed)
    signed = signer.sign(bytes(signing_string, encoding='utf8'))
    signature = base64.b64encode(signed.signature).decode()
    
    # Use invalid bap_id in the header
    invalid_bap_id = "invalid-bap-id.samhita.org"
    header = f'Signature keyId="{invalid_bap_id}|{UNIQUE_KEY_ID}|ed25519",algorithm="ed25519",created="{created}",expires="{expires}",headers="(created) (expires) digest",signature="{signature}"'
    return header

def test_nocs_api():
    print("TC_02: Signature validation - Invalid bap id in Authorization header")
    
    # Convert payload to minified JSON string
    request_body_raw_text = json.dumps(payload, separators=(',', ':'))
    
    # Generate authorization header with invalid bap_id
    auth_header = create_authorisation_header_with_invalid_bap(request_body_raw_text)
    
    # Prepare headers for the request
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'nocs-user/2.0.0',
        'Authorization': auth_header,
        'X-Gateway-Authorization': auth_header
    }
    
    # Make the API call
    try:
        response = requests.post(
            SETTLE_ENDPOINT,
            headers=headers,
            data=request_body_raw_text,
            timeout=30
        )
        
        print(f"Status: {response.status_code} | Txn: {transaction_id} | Msg: {message_id} | timestamp: {payload['context']['timestamp']}")
        print(f"Response: {json.dumps(response.json(), separators=(',', ':'))}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_nocs_api() 