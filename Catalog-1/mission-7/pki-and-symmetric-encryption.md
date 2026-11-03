# PKI (Public Key Infrastructure) and How It Compares to Symmetric Encryption

## What is a PKI?

A PKI is not an encryption algorithm but the **infrastructure around asymmetric keys**: it issues, signs, distributes, verifies and revokes **certificates**. A certificate binds a public key to an identity (person, server, organisation) and is signed by a certificate authority (CA), so that everyone who trusts the CA can trust the key without ever having met the owner.

Core building blocks:

- **Root CA and intermediate CAs:** the root certificate sits in the trust store of every OS/browser; signed intermediate CAs issue the end-entity certificates.
- **Registration:** before signing, the CA checks that the applicant controls the domain (Domain Validation, e.g. via ACME challenge) or, with more effort, who the organisation is (OV/EV).
- **Revocation:** CRL (revocation lists) and OCSP (online status query) allow compromised certificates to be invalidated before they expire.
- **Trust chain:** client verifies its signature back to a root CA known to be trustworthy (Root → Intermediate → End-Entity).

## Role of the PKI in IT Security

1. **Key distribution problem solved**, the main task. Symmetric encryption requires a secret channel for exchange; asymmetric keys are published, but alone they prove nothing. The PKI *attests* that this key belongs to this identity, allowing public keys to be used with strangers for the first time.
2. **Authentication:** in the TLS handshake, the server certificate proves to the client that it is really talking to this host and not to a man-in-the-middle. HTTPS for the entire web rests on this.
3. **Integrity of the chain of trust:** the signature of the CA makes every certificate tamper-proof; a modified certificate immediately invalidates the signature.
4. **Scalability of trust:** a trust store of a few dozen root CAs is enough to securely reach millions of servers, without bilateral agreements.
5. **Revocation and lifecycle management:** keys age and are stolen; the PKI makes this manageable (expiry dates, serial numbers, revocation, re-issue).
6. **Further applications beyond TLS:** code signing, document signing, S/MIME e-mail, VPN, IEEE 802.1X, wherever identity must be cryptographically proven.

## Comparison with Symmetric Encryption

| | **PKI (asymmetric + certificates)** | **Symmetric encryption (e.g. AES)** |
|---|---|---|
| Nature | Infrastructure for issuing and managing certificates | Pure encryption algorithm + key management |
| Keys | Key pairs (public + private); one pair per participant | One shared secret key |
| Key distribution | Solved by the PKI itself: certificate attests identity, public keys may be distributed openly | The core problem: the secret must reach the partner over a secure channel; no infrastructure can vouch for a *secret* |
| Identity | Provably attested by CA (or web of trust) | Not provable: whoever has the key is "trusted"; identity is not distinguishable |
| Speed | Slow: asymmetric operations, plus PKI overhead (handshake, validation, OCSP) | Very fast: suitable for bulk data |
| Scaling | N participants need N certificates; trust via shared CA hierarchy | N participants need N·(N−1)/2 bilateral keys, or one group key whose loss affects everyone |
| Revocation | Possible: CRL/OCSP can invalidate individual certificates | Not possible on the key itself; only a forced change of the key helps (re-keying) |
| Trust model | Central, delegated (CAs) or decentralised (Web of Trust) | None: must be established out-of-band |
| Application | Authentication, identity binding, key agreement (TLS server certificates, signatures, SSH keys) | Bulk encryption: traffic, disks, files, databases |

### Differences in application, in a nutshell

1. **Purpose:** symmetric encryption *encrypts data*; the PKI secures the *exchange of keys and the proof of identity* for this encryption.
2. **Who can use it:** PKI works with strangers (public keys + trust anchor); symmetric encryption only works with partners with whom one already shares a secret.
3. **Provenance:** the PKI can prove *who* is on the other end (certificate); symmetric encryption cannot attribute anything, because key possession is the only "proof".
4. **In practice both are used together (hybrid):** TLS is the prime example. The PKI part (certificate + signature) authenticates the server and protects the handshake; then a symmetric session key (e.g. AES-256-GCM) encrypts the actual data, because asymmetric encryption would be far too slow for bulk traffic.
5. **Without PKI, symmetric encryption needs manual key management:** pre-shared keys, Diffie–Hellmann exchange (protects against eavesdropping but not against MITM without certificates), or physically secured channels. The PKI automates exactly this point.

> **Conclusion:** asymmetric cryptography + PKI answers "how do we securely agree on a key and know who is on the other end?", while symmetric encryption answers "how do we encrypt large amounts of data quickly?". The PKI makes the asymmetric method usable at internet scale; symmetric encryption then does the actual work.