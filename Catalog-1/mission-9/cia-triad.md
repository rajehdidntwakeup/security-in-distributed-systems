# CIA Triad: Confidentiality, Integrity, Availability

## What is the CIA Triad?

The CIA triad is the three core goals of IT security. Every security measure protects one (or more) of them:

- **Confidentiality**: only authorized people can *read* data.
- **Integrity**: nobody can change data without being detected.
- **Availability**: data and systems are *usable* when needed.

Losing any one of the three means a security incident:

| Goal | Lost when... |
|---|---|
| Confidentiality | data leaks (stolen database, read email) |
| Integrity | data changes silently (tampered invoice, modified code) |
| Availability | system goes down (DDoS attack, ransomware encryption) |

## How Cryptography Helps

### Confidentiality: Encryption

Encryption scrambles data so only key holders can read it.

1. **HTTPS (TLS)**: browser ↔ web server traffic is encrypted, so a public Wi-Fi attacker cannot read passwords or cookies.
2. **Full-disk encryption (BitLocker, FileVault)**: a stolen laptop stays unreadable; the disk is ciphertext without the key.
3. **End-to-end encrypted messengers (Signal, WhatsApp)**: only sender and receiver hold the keys; even the provider cannot read messages.

### Integrity: Hashes and Signatures

Hashes detect change; digital signatures prove who approved data.

1. **Digital signatures on documents/software**: code signing proves an .exe comes from the vendor and was not modified (Windows checks signatures automatically).
2. **File integrity checks (SHA-256 checksums)**: Linux ISO downloads publish checksums; a different hash = corrupted or tampered file.
3. **Blockchain / tamper-evident logs**: each block contains the hash of the previous one; changing old data breaks the whole chain.

### Availability: Key Protection and Resilience

Cryptography cannot stop a DDoS, but it protects availability in other ways:

1. **Encrypted, tested backups**: ransomware encrypts live data, but an offline (or cloud-held-key) backup restores the system.
2. **Secure key management**: losing the only key = losing the data. Key escrow / key backups keep encrypted systems accessible.
3. **Authenticated protocols (e.g. TLS with rate limiting, DDoS protection services backed by certificates)**: fake servers cannot impersonate a real one, so traffic keeps going to the genuine service.

## Summary

| Goal | Main crypto tool | Example |
|---|---|---|
| Confidentiality | Encryption (AES, TLS, PGP) | stolen laptop unreadable |
| Integrity | Hashes + digital signatures | signed software update |
| Availability | Key management, backups | offline backup survives ransomware |

One line: **encrypt for secrecy, hash/sign for trust, manage keys and backups so data stays usable.**