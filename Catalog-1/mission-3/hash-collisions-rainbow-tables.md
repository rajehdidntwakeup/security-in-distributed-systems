# Hash Collisions, Rainbow Tables, Salting & Peppering

## Collision

A **collision** means two different inputs produce the same hash:

```
H(x) = H(y)  with  x ≠ y
```

A hash function maps a huge input space onto a fixed output space (SHA-256 → 2²⁵⁶ values). By the **pigeonhole principle**, collisions are always *possible* — a good hash only makes them *hard to find*. For password hashing the real attack is a **preimage** attack: given a hash, find the input. Human passwords are a tiny search space, so this is realistic.

## Rainbow Tables

A **rainbow table** is a precomputed lookup table for inverting hashes (hash → password). The attacker trades storage for speed: all guessing work is done in advance.

Simple idea: store every password → hash pair. Infeasible (≈ 95⁸ ≈ 6.6·10¹⁵ entries for 8-char passwords). Rainbow tables shrink this with **chains**:

```
p0 --H--> h0 --R--> p1 --H--> h1 --R--> ... --> pn
```

- **H** = hash, **R** = reduction function that deterministically maps a hash back to a new "password".
- The table stores only the **chain endpoints** (p0, pn) — megabytes instead of gigabytes.
- Lookup: walk the chain from the target hash until an endpoint matches, then rebuild from that chain's start and grab the plaintext.

Limits: one table per hash function and character set, and it does **not** work on salted hashes.

## Attacks

1. **Rainbow table attack** — attacker steals an unsalted password database, looks up the hashes in a prebuilt table, gets plaintext passwords in seconds. Same passwords show up as identical hashes even without cracking.
2. **Collision attack** — attacker builds two documents with the same hash: get the benign one signed, swap in the malicious one. Real examples: MD5 rogue CA certificate (2008), SHA-1 "SHAttered" (2017).

## Salting

A **salt** is a random, **non-secret** value generated per password and stored in plaintext right next to the hash:

```
stored = hash(salt || password)      →   user | salt | hash
```

Effect:

- Same password → different hash for every user.
- Rainbow tables die: attacker would need one table **per salt** — storage advantage gone.
- Cracking falls back to guessing each user's hash individually, at full cost.

## Peppering

A **pepper** is an additional random value that — unlike the salt — is **secret** and **not stored in the password database** (env variable, vault, HSM):

```
stored = hash(salt || password || pepper)
```

Effect:

- Attacker steals only the database (SQL injection, dump) → hashes are useless without the pepper.
- Attacker also steals the pepper → falls back to salt + slow hash.
- Trade-off: pepper must be managed; if lost, all passwords need a reset.

## Summary

| Measure | Protects against | Secret? | Stored |
|---|---|---|---|
| Salt (per password) | Rainbow tables | No | Next to hash |
| Pepper (global) | DB-only leaks | **Yes** | Outside DB |

Rule of thumb: never store passwords with a plain fast hash — use a slow, salted password hash (**Argon2id**, scrypt, bcrypt).