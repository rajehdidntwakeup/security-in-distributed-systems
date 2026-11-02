"""
Mission-4: Symmetric encryption with AES-256-GCM.

Shows:
  1. Encrypt and decrypt with one shared key.
  2. The tag detects tampering.
  3. Why reusing a nonce is fatal (two-time pad).

Requires:  pip install cryptography
Run:       python aes_demo.py
"""

import os
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# --- 1) Correct round-trip: one key, fresh nonce ---------------------------
key = AESGCM.generate_key(bit_length=256)   # 32 random bytes, never tell anyone
nonce = os.urandom(12)                      # 96-bit nonce, NEW for every message
message = b"Attack at dawn on bridge #42"

ciphertext = AESGCM(key).encrypt(nonce, message, None)   # last 16 bytes = tag
print("plaintext :", message.decode())
print("ciphertext:", ciphertext[:-16].hex())
print("tag       :", ciphertext[-16:].hex())

plaintext = AESGCM(key).decrypt(nonce, ciphertext, None)
print("decrypted :", plaintext.decode())

# --- 2) Tampering is detected ----------------------------------------------
tampered = bytes([ciphertext[0] ^ 1]) + ciphertext[1:]  # attacker flips one bit
try:
    AESGCM(key).decrypt(nonce, tampered, None)
except InvalidTag:
    print("tampering -> InvalidTag (plaintext never released)")

# --- 3) Nonce reuse = two-time pad ------------------------------------------
# Same key + same nonce gives the same keystream S:
#   C1 = P1 XOR S and C2 = P2 XOR S  =>  P1 XOR P2 = C1 XOR C2
p1 = b"Transfer 5000 EUR to Alice"
p2 = b"Transfer 9500 EUR to Mallory"
c1 = AESGCM(key).encrypt(nonce, p1, None)   # nonce deliberately reused
c2 = AESGCM(key).encrypt(nonce, p2, None)

known = b"Transfer 500"                     # attacker knows part of message 1
leaked = bytes(x ^ y for x, y in zip(c1, c2))[:len(known)]
leaked = bytes(a ^ b for a, b in zip(leaked, known))     # XOR recovers p2!
print("reused nonce -> leaked:", leaked.decode())