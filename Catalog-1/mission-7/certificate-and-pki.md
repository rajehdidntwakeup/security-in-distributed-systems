# Certificate and PKI: Self-Signed Certificate, Components and Requirements

This file accompanies the generated certificate in this folder:
- `selfsigned.crt`: the certificate (X.509, PEM/ASCII format)
- `selfsigned.key`: the matching **private key** (never share this!)
- `selfsigned.crt.txt`: human-readable dump of all fields (`openssl x509 -text`)

## Why certificates at all?

Public keys alone prove nothing: an attacker's public key can be swapped for Alice's. A **certificate** puts a public key together with **identification (who owns it) and a validity period**, signed by an issuer. The trust chain is: I trust the issuer, therefore I trust the certified key.

PKI (Public Key Infrastructure) as a whole means: certificate authorities (CAs) that issue and revoke certificates, registration procedures, trust stores in operating systems and browsers, and protocols such as OCSP and CRL for revocation.

## Role of a PKI in IT Security

- **Distribution of public keys:** CAs attest the identity behind each public key so that public keys can be used without prior negotiation. This is what enables HTTPS on the entire web.
- **Trust anchors:** Operating systems and browsers ship a trust store of root CAs, which is the implicit starting point of every TLS handshake.
- **Identity vs. encryption:** the certificate does not encrypt anything itself; it only establishes *who* the opposite side is, so that their key may be trusted.
- **Revocation:** a PKI can invalidate compromised certificates (CRL lists, OCSP queries).
- Examples: Let's Encrypt (automated, free, domain-validated), corporate-internal CAs, root CAs like DigiCert.

A **self-signed certificate** is the minimal variant: the issuer = the subject, i.e. the certificate vouches for itself. Useful and easy for testing, internal services and learning, but a browser warns *"Not trusted"* because no trusted third party confirms the identity.

## Creating the Certificate

Simplest variant with OpenSSL (one command). The CA variant with Let's Encrypt additionally requires a **publicly reachable server** and an ACME client, e.g. `certbot`, which proves domain ownership via an HTTP-01-challenge; this is not possible here, hence the self-signed route:

```bash
# 1. Generate RSA key pair + self-signed certificate in one step
openssl req -x509 -newkey rsa:2048 -keyout selfsigned.key -out selfsigned.crt \
    -days 365 -nodes -subj "//C=DE\CN=localhost\emailAddress=student@example.com"
# 2. Show all components
openssl x509 -in selfsigned.crt -text -noout > selfsigned.crt.txt
```

| Flag | Meaning |
|---|---|
| `-x509` | Output an X.509 certificate from a CSR-like process instead of only a CSR |
| `-newkey rsa:2048` | Generate a new RSA key pair with 2048 bits |
| `-days 365` | Valid for one year |
| `-nodes` | **No DES**, i.e. the private key is not password-protected |
| `-subj "//C=DE\CN=…"` | Distinguished Name (subject; on Windows `//` and `\` escape the slashes) |

## Requirements for a Certificate

For a certificate to be usable at all, the following requirements apply, independent of who signs it:

1. **Key material:** asymmetric key pair, nowadays at least RSA-2048 or an ECC curve (P-256); weak keys (512/1024 bit) are no longer accepted.
2. **Identification (subject):** for a publicly trusted CA, it must be proven that the applicant actually controls the domain (DV, Domain Validation: an ACME challenge such as a DNS TXT record or `http://<domain>/.well-known/…`). OV and EV add organizational checks. In the self-signed case, this identification is up to me, which is precisely the risk.
3. **A CA that signs the certificate:** the CA's own certificate chains up to a root in the trust store. With a self-signed certificate, the CA is *oneself*. Self-signed certificates are acceptable for own use as long as they are imported into the trust store manually.
4. **Validity period:** must be current; public web certificates are now limited (CA/Browser Forum: max. 47 days from 2029; Let's Encrypt shortens it to 10 days by 2029).
5. **Signature:** the complete certificate data is signed by the issuing CA (here: itself with its own key). Today only SHA-256 or stronger is used.
6. **Unique serial number:** set by the CA, required for revocation lists and OCSP.
7. **Adequate extensions (X.509 v3):** in particular *Key Usage*, *Extended Key Usage* (serverAuth) and *SAN (Subject Alternative Name)*, which is the only thing browsers still check for hostname matching.

## Components of Our Certificate

The content of `selfsigned.crt.txt` and what each part is for:

| Component | Value in this certificate | What it is for |
|---|---|---|
| **Version** | 3 (v3) | X.509 format version; v3 is required for extensions |
| **Serial Number** | `07:36:e8:7c:…` | Unique ID set by the issuer; used to identify certificates in CRL/OCSP |
| **Signature Algorithm** | sha256WithRSAEncryption | Algorithm used to sign the certificate; must be state of the art (SHA-1 is broken) |
| **Issuer** | `C=DE, CN=localhost, emailAddress=…` | Name of the CA that signed; here *identical to subject* (self-signed) |
| **Validity: Not Before / Not After** | `3 Nov 2026` – `3 Nov 2027` | Validity window; outside of it, the certificate is invalid |
| **Subject** | `C=DE, CN=localhost, emailAddress=…` | Identity of the certificate holder: Common Name (CN) used for hostname matching; today supplementary to the SAN |
| **Subject Public Key Info** | RSA 2048 bit, exponent 65537 | The actual **public key** of the holder, the subject of the whole attestation |
| **X509v3 Subject Key Identifier** | `B6:BB:1A:FA:…` | Hash of the holder's public key for faster key lookup during chain building |
| **X509v3 Authority Key Identifier** | `B6:BB:1A:FA:…` (same value) | Hash of the issuer's public key, used to find the right CA certificate when validating a chain; *identical here: issuer = subject = itself* |
| **X509v3 Basic Constraints (critical)** | `CA:TRUE` | Whether the certificate can be a CA (i.e., sign others). Critical = a client must reject an unknown value rather than ignore it. Here TRUE only because `openssl req -x509` defaults that way; for a server certificate, CA:FALSE would be correct |
| **Signature Value** | `2a:2d:89:f4:…` | The actual digital signature over all the above data, computed with the issuer key |
| **Extensions: Subject Alternative Name (SAN)** | (not set here) | Today the *decisive* field for host matching (`DNS:example.com`). If missing (our certificate), the browser falls back to CN and issues a warning |
| **Extensions: Key Usage / Extended Key Usage** | (not set) | Restricts use (digitalSignature, keyEncipherment …; serverAuth for TLS) |

### A note on our specific certificate

The Authority Key Identifier and Subject Key Identifier match, and **Issuer = Subject**: this is the machine-readable proof that the certificate is self-signed. CA:TRUE in Basic Constraints is an OpenSSL default; a "real" server certificate would state `CA:FALSE` here and would be signed by a separate CA certificate.

## What the Components Mean for Secure Communication (TLS as an Example)

1. **Subject/SAN (identity):** the client checks whether the requested host actually appears in the certificate. Without this check, every certificate could be presented for every site. Our `CN=localhost` certificate is thus only valid for `localhost`.
2. **Signature (integrity and chain of trust, authenticity):** the client verifies the issuer signature with the issuer's public key and follows the chain to a root CA in its store. This is what prevents an attacker from simply presenting their own certificate for another party (MITM). Self-signed certificates break exactly at this point: no third party confirms the identity.
3. **Validity (freshness):** expired certificates must be rejected, otherwise old (possibly already compromised) keys could be used further.
4. **Public Key (the basis of all key exchange):** during the TLS handshake, the server's *certified* public key is used to negotiate the symmetric session key. Only the possession of the corresponding private key allows the session key to be derived; the certificate thus indirectly protects the entire session.
5. **Signature Algorithm / Key Strength:** outdated algorithms (RSA-1024, SHA-1) mean a foreseeable break of the whole chain; modern algorithms are a prerequisite for the guarantees above to hold.
6. **Serial number + CRL/OCSP (revocation):** when a key is compromised, it can be *invalidated* again. Without serial numbers and revocation infrastructure, damage would be permanent.
7. **Basic Constraints / Key Usage:** prevent a server certificate from being misused as a CA, or a CA certificate from being used to sign code. This is what limits the *blast radius* when a key is stolen.

### Certificate vs. PGP

PGP solves the same problem, binding identity to a key, via a decentralized **Web of Trust**, whereas X.509/PKI relies on a trusted hierarchy of CAs. In both cases, the certificate/signature is the component that turns "some public key" into "the key of person X".

## Short Summary

A certificate binds a **public key** to an **identity and validity** and is signed by a CA. The individual parts (subject/SAN, signature, validity, public key, serial number, extensions) each cover a piece of what secure communication needs: correct identity, authenticity, freshness, key availability, revocation and restricted scope (misuse). PKI is the infrastructure that issues, distributes and revokes these certificates; our `selfsigned.crt` is the smallest possible variant, in which the "infrastructure" is the machine itself.