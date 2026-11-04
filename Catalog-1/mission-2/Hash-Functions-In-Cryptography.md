# Hash Functions in Cryptography: Why They Matter for Data Integrity

A **cryptographic hash function** (like SHA-256) takes any input of any size and produces a fixed-length digest. The same input always gives the same output, but you cannot go from the output back to the input.

## Key properties

- **Deterministic**: the same input always produces the same hash
- **One-way**: practically impossible to reverse (find the input from the digest)
- **Collision-resistant**: no two different inputs should produce the same hash
- **Avalanche effect**: changing one bit of the input changes the entire hash

## Why they matter for data integrity

- **Change detection.** If even a single bit of a file changes (by corruption, an editing error, or a malicious attacker), the hash changes completely. Comparing the hash before and after proves whether the data is intact.
- **Tamper evidence.** When a sender publishes a hash alongside a file, the receiver can recompute it. If the values differ, the file was modified in transit. This is how software download pages and package managers verify integrity.
- **Password storage.** Systems store the hash of a password, never the password itself. Hashing keeps the authentication system working while making sure the plain password is not exposed if the database leaks (a good practice is adding a unique salt to each password before hashing).
- **Digital signatures.** Documents are often too large to sign directly, so the hash of the document is signed instead. The signature then protects the full document, since any change invalidates the original hash.
- **Efficient comparison.** Comparing two fixed-length digests is fast and cheap, whether the inputs were two bytes or two gigabytes. This is how hash tables, blockchains (each block includes the hash of the previous one), and de-duplication systems work.

## Summary

Hash functions act as a **fingerprint for data**. Verifying this fingerprint is how systems detect corruption, prove files are untampered, store passwords safely, and attach digital signatures: all essential parts of ensuring data integrity.