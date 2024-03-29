import hmac
import hashlib


def verify_signature(body, secret_token, signature):
    secret_token = secret_token.encode("utf8")
    return (
        "sha1=" + hmac.new(secret_token, body, hashlib.sha1).hexdigest()
        == signature
    )
