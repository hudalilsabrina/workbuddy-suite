"""Pure standard-library RFC 6238 TOTP generator (Zero external dependencies)."""

import base64
import hashlib
import hmac
import struct
import time


def generate_totp(secret: str, interval: int = 30, digits: int = 6) -> str:
    """Generates a time-based one-time password (TOTP) from a base32 secret."""
    clean_secret = secret.replace(" ", "").upper()
    missing_padding = len(clean_secret) % 8
    if missing_padding:
        clean_secret += "=" * (8 - missing_padding)

    key = base64.b32decode(clean_secret)
    counter = int(time.time()) // interval
    msg = struct.pack(">Q", counter)

    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(code % (10**digits)).zfill(digits)
