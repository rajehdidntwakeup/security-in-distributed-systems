# Symmetric Encryption with AES-256-GCM

## The idea

Symmetric encryption = **one shared secret key**, locked with a padlock that same key opens.
Encrypt and decrypt both use the same key `k`: `E_k(plaintext) = ciphertext`, `D_k(ciphertext) = plaintext`.

That one line is also the problem: how do you hand someone the key without someone
else stealing it on the way? That is the **key distribution problem**: the main
weakness of all symmetric encryption.

## AES: a very good scrambling machine

**AES** is the world standard cipher (NIST, FIPS 197). You feed it 16 bytes and a key;
it scrambles them 14 times (for AES-256) with substitution and mixing steps so every
output bit depends on every input bit. Flip one plaintext bit → about **half the
ciphertext bits** flip (**avalanche effect**). No practical break of AES exists, and
brute force over 2^256 keys is hopeless. Nobody has ever broken AES itself.

## GCM: AES + a tamper-proof seal

AES encrypts only 16 bytes at a time, so a **mode of operation** strings blocks
together. The one to use today is **GCM**:

- encrypts in counter mode for **secrecy**,
- adds a **128-bit tag** for **integrity**: any change to the ciphertext fails
  verification before the plaintext is ever released,
- takes a **fresh 96-bit nonce per message** (a nonce = a unique number used once).

Never use ECB (identical blocks stay identical → patterns leak).

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

## How people actually break it

Nobody breaks the math. They break how it is used:

- **Nonce reuse:** same key + same nonce = same keystream for two messages →
  `C1 XOR C2 = P1 XOR P2`: a known plaintext reveals the other message. The tag
  breaks too. This is the classic real AES-GCM failure.
- **Key management:** keys in source code, passwords used as keys, keys left in disk
  or memory dumps. The most common cause of real-world AES "breaks".
- **No authentication:** using CBC or a plain stream without a tag → ciphertexts
  become malleable, error messages leak plaintexts (padding oracles).
- **Side channels:** timing/power attacks on implementations. Use vetted libraries,
  never roll your own AES.
- **Brute force:** 2^256 keys, out of reach even for quantum (Grover's algorithm
  "only" halves the effective key length; AES-256 stays safe).

## Symmetric vs asymmetric at a glance

| Aspect | Symmetric (AES-GCM) | Asymmetric (RSA/ECC) |
|--------|--------------------|----------------------|
| Keys | One shared secret | Key pair (public + private) |
| Key distribution | Hard: needs secret channel | Easy: public key is public |
| Speed | Very fast (GB/s) | Slow, 100–1000× |
| Bulk data | Yes, arbitrary length | No, limited to key size |
| Keys for n people | ~n²/2 | n |
| Quantum | AES-256 still safe | Broken (Shor) |

Real systems use both (**hybrid encryption**, TLS 1.3): asymmetric crypto
authenticates the peers and derives the session key, then AES-GCM encrypts all the
data. Asymmetric says *who*, symmetric moves *the data*.
