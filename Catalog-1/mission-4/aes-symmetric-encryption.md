# Symmetric Encryption with AES-256-GCM

## Principle

Symmetric encryption uses **one shared secret key** for encryption and decryption:
`E_k(plaintext) = ciphertext` and `D_k(ciphertext) = plaintext` (same `k` on both sides).
Both parties must already share the key through a confidential channel first: this **key
distribution problem** is the main weakness of symmetric schemes.

**AES** (NIST standard FIPS 197) is today's standard block cipher: 128-bit blocks,
keys of 128/192/256 bits (→ 10/12/14 rounds). Each round applies:
**SubBytes** (non-linear S-box substitution) → **ShiftRows** + **MixColumns** (diffusion)
→ **AddRoundKey** (XOR with a derived round key). 14 rounds produce an avalanche effect:
flipping one plaintext bit changes roughly half the ciphertext bits. No practical break
of full AES exists; brute force over 2^256 keys is out of reach.

A block cipher alone encrypts only 16 bytes, so it runs in a **mode of operation**.
Never ECB (identical blocks stay identical → patterns leak). Use **GCM**: AES in counter
mode for secrecy plus the GHASH MAC for integrity. GCM needs a **fresh 96-bit nonce per
message**, outputs a **128-bit authentication tag** (any tampering is detected), and
optionally authenticates **AAD** (associated data: authenticated, not encrypted).

## Code Example (Python, `cryptography`)

```python
import os
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

key = AESGCM.generate_key(bit_length=256)     # 32 random bytes
nonce = os.urandom(12)                        # fresh per message!

ct = AESGCM(key).encrypt(nonce, b"Attack at dawn", None)
pt = AESGCM(key).decrypt(nonce, ct, None)     # tag verified automatically

ct[0] ^= 1                                    # attacker flips one bit...
AESGCM(key).decrypt(nonce, ct, None)          # ...raises InvalidTag
```

## Attack Scenarios

- **Brute force:** 2^256 keys, hopeless and never the real weakness. (Quantum: Grover
  halves the key length, so AES-256 stays safe; RSA/ECC would not.)
- **Nonce reuse in GCM/CTR:** same key + same nonce = same keystream, a two-time pad.
  `C1 XOR C2 = P1 XOR P2`: the keystream cancels, a known plaintext leaks the other
  message without breaking AES. Reuse also enables GCM tag forgeries.
- **Missing authentication:** without a tag, ciphertexts are malleable and CBC
  decryption error messages leak plaintexts (padding oracle attacks).
- **Key management failures:** keys in source code, passwords instead of random keys,
  keys left in memory: the usual real-world cause of AES "breaks".
- **Side channels:** timing/power attacks on implementations; rely on vetted, constant-time
  libraries, never roll your own AES.

## Differences from Asymmetric Encryption

| Aspect | Symmetric (AES-GCM) | Asymmetric (RSA/ECC) |
|--------|--------------------|----------------------|
| Keys | One shared secret | Key pair (public + private) |
| Key distribution | Hard: needs secret channel | Easy: public key is public |
| Speed | Very fast (GB/s) | Slow, 100–1000× |
| Bulk data | Yes, arbitrary length | No, limited to key size |
| Keys for n people | ~n²/2 | n |
| Quantum | AES-256 still safe | Broken (Shor) |

In real systems they work together (**hybrid encryption**, e.g. TLS 1.3): asymmetric
crypto authenticates the peers and derives the session key over an open channel, then
AES-GCM encrypts the whole session. Asymmetric says *who*, symmetric moves *the data*.