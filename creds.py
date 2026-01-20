#!/usr/bin/env python3
import base64
import datetime
import os
import dotenv
import nacl.encoding
import nacl.hash
from nacl.bindings import crypto_sign_ed25519_sk_to_seed
from nacl.signing import SigningKey

dotenv.load_dotenv()

# API endpoint
SETTLE_ENDPOINT = "https://ondcnbbl.npci.org.in/nocs/v2/settle"
REPORT_ENDPOINT = "https://ondcnbbl.npci.org.in/nocs/v2/report"


SUBSCRIBER_ID = os.environ.get('SUBSCRIBER_ID')
UNIQUE_KEY_ID = os.environ.get('UNIQUE_KEY_ID')
PRIVATE_KEY = os.environ.get('PRIVATE_KEY')
BUYER_KEY = "G0Pme72u8Y1MwxHqvY4iBW+7VPtJ7dsX7SGs6zZ5yvVIzdRAyHR6YkwHG2ufOE+12lsbJRwBF4Hqd7dUEOZZkg=="


COLLECTOR_APP_ID = os.environ.get('SUBSCRIBER_ID')
RECEIVER_APP_ID = "SellerAppTestdata12.com"
DIFFERENT_COLLECTOR_APP_ID = "different-collector.samhita.org" # Different collector app id


BAP_ID = os.environ.get('BAP_ID')
BAP_URI = os.environ.get('BAP_URI')
BPP_ID = "sa_nocs.nbbl.com"
BPP_URI = "https://sa_nocs.nbbl.com/nocs_test"

def hash_message(msg: str):
    HASHER = nacl.hash.blake2b
    digest = HASHER(bytes(msg, 'utf-8'), digest_size=64, encoder=nacl.encoding.Base64Encoder)
    digest_str = digest.decode("utf-8")
    return digest_str

def create_signing_string(digest_base64, created=None, expires=None):
    if created is None:
        created = int(datetime.datetime.now().timestamp())
    if expires is None:
        expires = int((datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp())
    signing_string = f"""(created): {created}
(expires): {expires}
digest: BLAKE-512={digest_base64}"""
    return signing_string

def sign_response(signing_key, private_key):
    private_key64 = base64.b64decode(private_key)
    seed = crypto_sign_ed25519_sk_to_seed(private_key64)
    signer = SigningKey(seed)
    signed = signer.sign(bytes(signing_key, encoding='utf8'))
    signature = base64.b64encode(signed.signature).decode()
    return signature

def create_authorisation_header(SUBSCRIBER_ID,request_body,KEY, created=None, expires=None):
    created = int(datetime.datetime.now().timestamp()) if created is None else created
    expires = int((datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp()) if expires is None else expires
    signing_key = create_signing_string(hash_message(request_body),
                                        created=created, expires=expires)
    signature = sign_response(signing_key, private_key=KEY)

    header = f'Signature keyId="{SUBSCRIBER_ID}|{UNIQUE_KEY_ID}|ed25519",algorithm="ed25519",created="{created}",expires="{expires}",headers="(created) (expires) digest",signature="{signature}"'
    return header

def get_headers(SUBSCRIBER_ID,request_body,KEY):
    auth_header = create_authorisation_header(SUBSCRIBER_ID,request_body,KEY)
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'nocs-user/2.0.0',
        'Authorization': auth_header,
        'X-Gateway-Authorization': auth_header
    } 