# Asymmetric Encryption with RSA

## Principle

Asymmetric encryption uses a **key pair**: a `public key` for encryption (freely
shareable) and a mathematically linked `private key` for decryption (secret).
Nobody who holds only the public key can decrypt: this solves the **key
distribution problem** of symmetric ciphers: the key no longer has to be
exchanged over a confidential channel beforehand.

**RSA** (Rivest–Shamir–Adleman, 1977) security rests on the **factoring
problem**: multiplying two large primes is easy, recovering them from the
product is practically impossible.

### How the algorithm works

1. **Key generation**
   - Choose two large random primes `p`, `q` (each ~1024 bits for RSA-2048).
   - Modulus: `n = p · q`
   - Euler's totient: `φ(n) = (p−1)(q−1)`
   - Public exponent `e`: usually the fixed value 65537 (prime, fast `e = 2^16+1`)
   - Private exponent: `d = e⁻¹ mod φ(n)` (the modular inverse of `e`)
   - Public key = `(n, e)`, private key = `(n, d)`; `p, q, φ(n)` stay secret or are erased.

2. **Encryption** of message `m` (as integer, 0 ≤ m < n):
   `c = m^e mod n`

3. **Decryption** works because `e·d ≡ 1 (mod φ(n))`, so `c^d ≡ m^(ed) ≡ m (mod φ(n))`:
   `m = c^d mod n`

Only the owner of `d` can reverse the exponentiation; everyone else would need
to factor `n` into `p` and `q` to compute `φ(n)` and derive `d`.

### Padding: why textbook RSA is never used

Raw RSA is **deterministic** (same message → same ciphertext) and
**malleable** (`c' = c · r^e mod n` decrypts to `m·r`: an attacker can
multiply a message by a chosen factor without knowing it). Therefore real
systems use a padding scheme:

- **OAEP** (Optimal Asymmetric Encryption Padding, RFC 8017): the modern
  standard. Injects randomness (every encryption produces a different
  ciphertext from the same plaintext) and provably resists chosen-ciphertext
  attacks. This is what the code example uses.
- **PKCS#1 v1.5**: legacy, still widely deployed but has known attack history.
- For **authenticity** the same key pair is used in reverse with **PSS padding**:
  sign with the private key, verify with the public key (used in the demo).

## Attack Methods

| Attack | Approach | Defense |
|---|---|---|
| Factoring | Recover `p, q` from `n`. Best known: General Number Field Sieve; RSA-768 (232 digits) was factored in 2009 on hundreds of PCs over months | Use ≥ 2048 bit; 3072+ for long-term secrets; RSA-1024 is broken territory |
| Bleichenbacher / padding oracle ("ROBOT") | Send manipulated ciphertexts, observe whether an SSL/TLS server reports a padding error → adaptive chosen ciphertext attack recovers plaintext | Use OAEP; servers must return constant errors/timing |
| No-padding/textbook attacks | Small `e` (often 65537) without padding: low-entropy message m³ < n → just send `m`; same message sent to `e` recipients → Håstad broadcast attack | Always use OAEP with fresh randomness |
| Small private exponent (Wiener) | Choose `d` too small for faster decryption → `d` recoverable from `(e, n)` | Use standard key generation, `d` ≈ size of `n` |
| Timing / cache side channels | Measure how long modular exponentiation takes per bit/branch of `d` | Constant-time implementations (in the `cryptography`/OpenSSL library) |
| Weak key generation | Reused or low-entropy primes; shared `p` between two users' moduli → common factor via GCD, instantly broken | Cryptographically secure RNG, fresh primes per key |
| MITM on key exchange | RSA does not authenticate by itself: attacker swaps the public key in transit, decrypts everything | PKI / certificates / key fingerprints (TLS does this) |
| Quantum (Shor's algorithm) | A sufficiently large quantum computer factors `n` in polynomial time | Migrate PQC standards (e.g. ML-KEM/Kyber); hybrid schemes already in TLS deployments |

## Code Example (Python, `cryptography`)

See `rsa_demo.py`. Core:

```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

# Key generation: public (n, e), private (n, d)
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

# Encrypt with PUBLIC key (OAEP; never raw RSA)
ciphertext = public_key.encrypt(
    b"Attack at dawn",
    padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                 algorithm=hashes.SHA256(), label=None),
)

# Decrypt with PRIVATE key
plaintext = private_key.decrypt(ciphertext, padding.OAEP(
    mgf=padding.MGF1(algorithm=hashes.SHA256()),
    algorithm=hashes.SHA256(), label=None))
```

Notes: RSA-2048/OAEP/SHA-256 fits one block of 214 bytes. Key generation is
orders of magnitude slower than encryption/decryption and is normally done
once per identity.

## Comparison with Symmetric Encryption (AES)

| | **RSA (asymmetric)** | **AES-256-GCM (symmetric)** |
|---|---|---|
| Keys | Key pair: `(n, e)` public, `d` private | One shared secret `k`, same for encrypt + decrypt |
| Key exchange | No secure channel needed; public key sent openly | **Key distribution problem**: `k` must already be shared over a confidential channel |
| Speed | Very slow (modular exponentiation with 2048-bit numbers), roughly 1000–10000x slower | Very fast, hardware instructions (AES-NI), GB/s throughput |
| Payload size | One block only: 214 bytes message per 256-byte RSA-2048 ciphertext | Unlimited (block cipher in GCM stream mode) |
| Security primitive | Factorization problem (only RSA-specific attacks + quantum known) | Brute force over 2^256 keys; no practical break |
| Who can encrypt | Anyone with the public key → ideal for broadcast | Only holders of the secret key |
| Authenticity/integrity | Via signature (PSS) with private key, also non-repudiable | Via built-in GCM tag, any tampering is detected |
| Key management for N users | N key pairs; pairwise comm. needs `2N` keys total | Pairwise: `N·(N−1)/2` secret keys, explodes at scale; usually solved with a KDC/KMS |

### How they are applied in practice: hybrid encryption

The differences mean the two are used **together**, not competitively, e.g.
HTTPS/TLS, Signal, PGP, encrypted zip:

1. Alice generates a fresh **AES session key + nonce** per message.
2. She encrypts the bulk data with **AES-GCM** (fast, any size).
3. She encrypts *only the session key* with Bob's **public RSA key** (small payload, fits one block).
4. Bob recovers the AES key with his private key, then decrypts the data symmetrically.

Distribution of labor: RSA solves **key distribution and authenticity**
(small, slow, done once), AES does the **actual bulk encryption**
(large, fast, done per message). Neither alone covers both needs:

- AES alone: fast, but "how do we agree on the key?" is unsolved.
- RSA alone: key exchange solved, but too slow and too small-capacity for data.

## Key Takeaways

- RSA = key pair, asymmetric; security from factoring a `n = p·q` modulus.
- Never raw/textbook RSA → always OAEP (encryption) or PSS (signatures).
- ≥ 2048 bit keys; quantum computers are the long-term threat (→ PQC migration).
- In the real world RSA encrypts the AES key, AES encrypts the data (hybrid).