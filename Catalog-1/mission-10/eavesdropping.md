# Eavesdropping and the Padlock

## Part 1: Eavesdropping on Unencrypted Connections

Unencrypted traffic (plain HTTP) is like a postcard: everyone on the path can read it.

| Method | How it works |
|---|---|
| **Passive sniffing** | Anyone on the same network (Wi-Fi hotspot, LAN) captures packets with a tool like Wireshark. No attack noise, hard to notice. |
| **Man-in-the-middle (MITM)** | Attacker sits between client and server (e.g. ARP spoofing on LAN, fake "free Wi-Fi" hotspot, evil twin) and forwards traffic while reading it. |
| **Replay / session hijacking** | Attacker reuses captured session cookies or tokens to pretend to be the victim, without breaking the password itself. |
| **Network-internal observers** | ISPs, router admins, DNS-resolver operators, proxies see all plain traffic. |
| **Malware / Trojan** | Malicious program on the victim's device reads data directly, even before it leaves the machine. |

### What leaks in plain HTTP

- Login forms: usernames and passwords in cleartext.
- Cookies and session tokens (enable hijacking).
- Personal data, messages, search queries, form inputs.
- Full URLs and metadata (which sites you visit, how often).

## Part 2: Eavesdropping on Encrypted Connections

Encryption does not make traffic invisible, only unreadable. Attackers go for **metadata**, **keys**, or **endpoints** (not the ciphertext itself).

| Method | How it works |
|---|---|
| **Traffic analysis** | Even encrypted, attacker sees who talks to whom, when, how much, which IPs/ports (SNI used to leak the domain name too). Patterns can still identify sites or actions. |
| **Stealing the key** | Instead of breaking AES (practically impossible), attacker steals the session keys from memory or disk (e.g. **Heartbleed**, 2014: leaked memory chunks contained keys and cookies). |
| **Endpooint compromise (malware)** | If the virus sits on the user's device, it reads data *before* encryption and *after* decryption. Crypto is bypassed, not broken. |
| **Downgrade attacks** | Trick client and server into falling back to weak/no encryption (e.g. old **SSLv2/SSLv3**, POODLE). Modern TLS 1.3 prevents this. |
| **MITM with fake certificate** | Attacker presents their own certificate and decrypts/re-encrypts traffic. Works only if the victim accepts the fake cert (ignoring the browser warning, clicking "Proceed anyway", planted root CA, corporate proxy). |
| **Human weakness (phishing)** | Not crypto at all: attacker gets the secret (password, MFA code) by tricking the user. Encrypted delivery of stolen data is irrelevant. |

### Key insight

Attacking the math (AES, RSA) is hopeless. Real attacks hit **weak points around the crypto**: metadata, keys in memory, endpoints, downgrades, and humans.

## Part 3: Evaluation of the Statement

> "A closed padlock in the browser bar means that the connection is secure and that the visited domain is authentic."

**The statement is false in both halves.** The padlock is necessary but **not sufficient**.

### What the padlock actually tells you

The TLS connection to *something* is encrypted, and the certificate chain is valid for the domain shown in the address bar (that part is real). That is all.

### Why the connection is NOT automatically "secure"

- **The server itself can be malicious**: phishing sites get HTTPS for free. Let's Encrypt issues every fraudster a valid certificate, no questions asked. `https://paypal-account-verify.example.com` shows a padlock and is still a scam.
- **Malware on the site** (drive-by downloads) rides encrypted: the padlock does not inspect content.
- The encryption protects only the **transport**, not you from fraud or content.

### Why "authentic" is misleading

- The padlock certifies the **domain name matches the certificate**, not that the domain is the one you *mean* or *trust* (typosquatting, lookalike domains, subdomain tricks).
- Users misread the padlock as a **trust seal**: surveys show many believe it promises a legitimate business. A padlock next to "Won a lottery, pay here" is worth nothing.

### A padlock helps, but you must also check

1. Does the address bar show the **exact domain** you expect (no lookalikes)?
2. No browser warning ignored (`NET::ERR_CERT_AUTHORITY_INVALID` must never be clicked away).
3. Modern TLS (no downgrade warnings).

## Summary

| Question | Answer |
|---|---|
| Padlock = encrypted connection to the shown domain? | Yes |
| Padlock = site content safe? | No |
| Padlock = honest operator? | No |
| Padlock = domain authentic? | Only in the technical sense: name matches the certificate |

**One line:** the padlock proves *encryption to that domain name*, nothing more — trust comes from checking the domain itself, not from the lock.