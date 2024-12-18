import hashlib
import hmac

def verify_signature(payload_body, secret_token, signature_header):
    '''
    Webhook signature verification from GitHub docs:
        https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries#python-example
    Modified for use here
    '''
    if not signature_header:
        return False
    hash_object = hmac.new(secret_token.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature_header):
        return False
    else:
        return True
