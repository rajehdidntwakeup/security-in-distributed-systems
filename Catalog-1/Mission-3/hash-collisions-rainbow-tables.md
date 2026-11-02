# Hash Collisions, Rainbow Tables, Salting & Peppering

## 1. Collisions and Rainbow Tables

### Collision

A **collision** occurs when two different inputs produce the same hash value:

$$H(x) = H(y) \quad \text{with} \quad x \neq y$$

The root cause is the **pigeonhole principle**: a hash function converts an arbitrarily large input space into a fixed-size output space (e.g., SHA-256 → $2^{256}$ possible values). Since the input space is larger than the output space, infinitely many inputs must map to the same hash.

Relevant types of collision attacks:

- **Collision:** find *any* pair $x, y$ with $H(x) = H(y)$. Feasible with the birthday attack in roughly $2^{n/2}$ time (n = hash length).
- **Second preimage:** given a fixed $x$, find $y \neq x$ with $H(x) = H(y)$.
- **Preimage:** given a hash value $h$, find any $x$ with $H(x) = h$.

Note the security difference: for a *general* 256-bit hash, birthday attacks and second preimages do not realistically break SHA-256. However, **password hashing is essentially a preimage problem over a tiny input space**, humans choose from a few trillion possible passwords, not $2^{256}$. This is where rainbow tables come in.

### Rainbow Tables

A **rainbow table** is a precomputed lookup table that lets an attacker invert hash values — find the plaintext (usually a password) for a given hash — without brute-forcing at attack time. All computation was done in advance ("trade time for space").

**Why not a simple lookup table?** Storing every password → hash pair is infeasible: all character combinations up to length 8 with 95 printable ASCII characters ≈ $95^8 \approx 6.6 \cdot 10^{15}$ entries. Rainbow tables use **time-memory trade-off** to shrink the table size dramatically.

**How they work — chains and reduction functions:**

1. Start with a plaintext $p_0$ (e.g., `aaaaaa`).
2. Hash it: $h_0 = H(p_0)$.
3. Apply a **reduction function** $R$ that maps the hash back to a new *deterministic* plaintext: $p_1 = R(h_0)$ (e.g., take the first 6 hex digits as the next "password").
4. Repeat: $h_1 = H(p_1)$, $p_2 = R(h_1)$, ... for a fixed chain length (e.g., 1000).

Table stores **only the endpoints** (start plaintext $p_0$ and final plaintext $p_n$), not intermediate values — this is where the space is saved:

```
p0 --H--> h0 --R--> p1 --H--> h1 --R--> ... --H--> hn-1 --R--> pn
```

**Lookup procedure:** given target hash $h$:

1. Apply $R$, then $H$, then $R$ ... starting from $h$, iterating up to the chain length, hoping to land on a stored endpoint $p_n$.
2. If an endpoint matches, start from the corresponding $p_0$ and rebuild the chain, checking every hash along the way for $h$.
3. When found $h = H(p_i)$, then $p_i$ is the recovered preimage (password).

Different tables use **different reduction functions** to limit chain merging.

**Limits:** rainbow tables are hash-specific (separate table per algorithm) and only cover a given character set/length range. They also do **not** work on salted hashes — the salt changes the hash input and would require a table per salt value, which destroys the storage advantage.

## 2. Attacks with Collisions and Rainbow Tables

### Attack via rainbow tables

Against an **unsalted** password database, the attack is trivial:

1. Attacker steals password file: `user: e3b0c44298fc1c14...`.
2. Looks up the hash in a prebuilt rainbow table (many downloadable, e.g., for MD5/SHA-1/NTLM).
3. Gets the plaintext password in seconds, logs in as that user.

Because users reuse passwords, cracks also work on email, VPN and other accounts. Speed of modern GPU/ASIC hash cracking (billions of guesses per second against plain MD5/SHA-256) makes unsalted fast hashes obsolete.

### Attack via collisions (chosen-prefix)

Where a hash collision exists between $H(m_1) = H(m_2)$ with attacker-controlled $m_1, m_2$, an attacker can do "transferability of trust" attacks:

- **Digital signature abuse:** get a benign document $m_1$ signed (contract, thesis), then swap in malicious $m_2$ that has the same hash and therefore a valid signature. This is exactly what happened with the MD5 collision attack against a rogue CA certificate (2008) and the SHAttered SHA-1 collision (2017).
- **File integrity bypass:** supply a file that passes a MD5 checksum comparison, e.g., in software update distribution.
- **Password hash reuse:** two accounts share a password → identical unsalted hashes leak this from the stolen database even without cracking.

### Defenses — Salting and Peppering

Because the threat for passwords is *preimage* over a tiny space, the fix is not "use SHA-512" but "make the input space per-user unique and slow".

#### Salting

A **salt** is a random, non-secret value (e.g., 16 bytes) generated per password, stored **in plaintext** next to the hash:

```
stored = hash(salt || password)   →   user | salt | hash
```

Effects:

- Identical passwords no longer produce identical hashes → no visible duplicate passwords, and **reduction attacks on the whole database fail**.
- Rainbow tables become useless: attacker would need one table *per salt value* (per user) — storage advantage is destroyed.
- Precomputed/GPU cracking still possible, but only one hash at a time, at full cost for each user.

Important: salt is **not secret** — it must be unique and random, that is its entire effect. It does not slow down cracking of a single password on its own.

#### Peppering

A **pepper** is an additional random value that, unlike the salt, is **secret** and **not stored in the password database** — it lives outside, e.g., in an environment variable, a config file inaccessible to the database, or an HSM:

```
stored = hash(salt || password || pepper)
```

or with HMAC:

```
stored = HMAC-SHA256(key = pepper, salt || password)
```

Effects:

- If the attacker steals **only the database** (SQL injection, leak), the hashes are useless without the pepper — password guessing is impossible, not just slow.
- If attacker also steals the pepper, protection falls back to "salt + slow hash".
- Downside: pepper must be managed/rotated; if lost, all passwords are unrecoverable and users must be reset (usually acceptable — password reset exists anyway).

#### Slow, memory-hard hash functions

Salting stops precomputation; slowness stops online/GPU brute force. Use purpose-built password hashes that support salting by design and are CPU/memory-intensive:

- **Argon2id** (current recommendation, winner of the Password Hashing Competition)
- **scrypt** (memory-hard)
- **bcrypt** (1923-style cost factor, widely proven)
- *PBKDF2* only when standard compliance demands it (weaker — GPU-friendly)

And the summary rule of thumb: **never store passwords with a plain fast hash like MD5/SHA-256/SHA-512**, always as `Argon2id(password, salt [, pepper])`.

## 3. Summary Table

| Measure | Protects against | Secret? | Stored where? |
|---|---|---|---|
| Collision-resistant hash (SHA-256+) | Signature/integrity forgery | — | — |
| Salt (per-password, random) | Rainbow tables, cross-user pattern leaks | No | Next to hash |
| Pepper (global, random) | Database-only leaks | **Yes** | External to DB |
| Slow memory-hard hash (Argon2id) | Offline brute force | — | — |