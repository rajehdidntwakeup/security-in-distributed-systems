"""
RSA-2048 encryption demo (Python, `cryptography` library).

Textbook RSA (c = m^e mod n, raw) is NEVER used on real data: it is
deterministic and malleable. Real RSA always uses a padding scheme
here OAEP (Optimal Asymmetric Encryption Padding), the modern standard
(RFC 8017). Run with:  python rsa_demo.py
"""

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature

message = b"Attack at dawn"

# ---- 1. Key generation (one time, the expensive step) --------------------
# RSA-2048 is the current minimum; 3072+ for long-term secrets.
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

# The public key may be shared openly; only the private key must stay secret.
pem_pub = public_key.public_bytes(
    serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
)
pem_priv = private_key.private_bytes(
    serialization.Encoding.PEM,
    serialization.PrivateFormat.PKCS8,
    serialization.NoEncryption(),  # real systems: encrypt with a passphrase!
)

# ---- 2. Encryption (by anyone who has the public key) --------------------
ciphertext = public_key.encrypt(
    message,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    ),
)
print(f"ciphertext ({len(ciphertext)} bytes): {ciphertext.hex()[:40]}...")

# ---- 3. Decryption (only with the private key) ---------------------------
plaintext = private_key.decrypt(
    ciphertext,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    ),
)
print(f"decrypted: {plaintext.decode()}")
assert plaintext == message

# ---- 4. What an attacker (without the private key) can do ----------------
# 4a. Tamper with the ciphertext. OAEP randomization + integrity checks make
#     this fail loudly instead of decrypting to a corrupted message.
tampered = bytearray(ciphertext)
tampered[0] ^= 1
try:
    private_key.decrypt(bytes(tampered), padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    ))
    print("tampered ciphertext accepted (BAD!)")
except ValueError:
    print("tampered ciphertext rejected: ValueError (decryption failed)")

# 4b. RSA encryption only handles ONE block (214 bytes for 2048-bit OAEP).
#     Real-world practice is hybrid encryption: RSA encrypts a random AES
#     session key, AES-GCM encrypts the bulk data. Shown via signing here:
signature = private_key.sign(
    message,
    padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
    hashes.SHA256(),
)
try:
    public_key.verify(
        signature, message,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256(),
    )
    print("signature valid (authenticity + integrity, uses same key pair)")
except InvalidSignature:
    print("signature invalid")