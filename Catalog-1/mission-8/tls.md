# TLS (Transport Layer Security): Functions, Benefits and Integration

This file accompanies `tls_demo.py`: the smallest working TLS integration that uses the certificate from Mission 7.

## What is TLS?

TLS is the successor of SSL and today secures practically all data traffic on the internet, from HTTPS to mail and VPN connections. TLS sits between the transport layer (TCP) and the application layer and establishes an **encrypted, authenticated channel** that even a man-in-the-middle cannot read or modify.

## Functions of TLS

| Function | How TLS achieves it |
|---|---|
| **Confidentiality** | All application data is encrypted symmetrically, today e.g. with AES-256-GCM. The key is negotiated per session and never appears on the wire. |
| **Authentication** | The server presents a certificate. The client verifies the CA signature and whether the host matches the Subject/SAN. Only the holder of the private key can complete the handshake. |
| **Integrity** | Every record is AEAD-protected: any single altered bit causes decryption to fail (tag verification). |
| **Key exchange** | (EC)DHE provides **forward secrecy**: session keys are derived from fresh ephemeral keys and remain secret even if the server's private key is later stolen. |
| **Perfect backward compatibility** | Version and cipher negotiation at the beginning; outdated versions (TLS 1.0/1.1) are rejected today. |

## Benefits in Practice

1. **Protection against eavesdropping** on the route: Wi-Fi hotspot, ISP, backbone. The metadata (server name until ECH, IPs, sizes) remains visible, the content does not.
2. **Protection against manipulation** during transmission (content injection, DNS hijacking of results).
3. **Proof of identity:** the user knows that this is actually the intended server, not an imitator. This is what makes online banking and e-commerce possible.
4. **Compliance and standards:** GDPR encryption of transmissions, PCI-DSS and similar requirements demand TLS.
5. **Low integration cost, high benefit:** one context + one certificate, as the sample application below shows.
6. **Session resumption:** TLS 1.3 (0-RTT) reduces the handshake overhead for repeat visitors.

## Requirements for the Implementation

1. **A private key** (self-signed from mission 7: `selfsigned.key`) that never leaves the server side.
2. **A certificate** (`selfsigned.crt`) that attests the server identity. Self-signed is OK for a lab/test; production uses a CA-signed certificate (Let's Encrypt etc.), because clients must be able to verify the chain of trust.
3. **Name agreement:** the client must call the server under the name that the CN/SAN of the certificate designates, here `localhost`. Any other name would fail host matching.
4. **Current TLS library:** Python's `ssl` module wraps OpenSSL; `PROTOCOL_TLS_SERVER` selects the highest version supported mutually (here verified: **TLS 1.3** with `TLS_AES_256_GCM_SHA384`).
5. **A free TCP port** and its firewall rules: the sample uses `8443`, the classic HTTPS test port (`443` needs admin rights on many systems).
6. **Key hygiene:** no rights for foreign users on the key file, no key in Git, private key not readable from outside.

## The Individual Steps for the Implementation

The complete steps of the sample application, each line in `tls_demo.py` corresponds to one step:

1. **Build the HTTP application, plain HTTP first,** as usual: routes `/` and `/health`, status code plus body. The HTTP code remains untouched by TLS (`class Handler`).
2. **Create an SSL context**, the central configuration point: `ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)`. It controls TLS version, ciphers and certificate.
3. **Load the certificate chain:** `context.load_cert_chain(certfile=..., keyfile=...)` with the Mission-7 pair. The server now owns identity + private key.
4. **Wrap the listening socket:** `context.wrap_socket(server.socket, server_side=True)` wraps the plain TCP listener with TLS. Every byte that leaves or arrives now goes through the TLS record layer, transparent for the HTTP code.
5. **Serve.** With a browser, the self-signed warning appears once (expected: no CA confirms the identity of `localhost`); after importing the certificate into the trust store, the warning disappears.

Everything needed in Python (step 2 to 4 in full):

```python
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="selfsigned.crt", keyfile="selfsigned.key")
server = http.server.HTTPServer(("localhost", 8443), Handler)
server.socket = context.wrap_socket(server.socket, server_side=True)
```

This is the **whole TLS integration**: three configuration lines. Nothing in the application code needs to change because TLS operates below it. That is the architectural benefit of the layer model.

## Run and Verify

```bash
python tls_demo.py            # serves on https://localhost:8443
curl -sk https://localhost:8443/health
# {"status": "ok", "tls": true}
openssl s_client -connect localhost:8443 -servername localhost </dev/null
#   Protocol  : TLSv1.3
#   Cipher    : TLS_AES_256_GCM_SHA384
#   Verify return code: 18 (self-signed certificate)
```

- `curl -k` / `Verify return code 18` shows exactly the difference between encryption and authentication: the connection is **encrypted** (TLS succeeds), but the identity is **not attributable to a third party** (self-signed). Production would use a CA certificate here.
- The measured result matches mission 4: the actual data runs through AES-256-GCM, and mission 7 provides the identity layer. TLS 1.3 simply combines both.

## Limitations of This Minimal Sample (and What Production Adds)

| Sample app | Production server |
|---|---|
| Self-signed certificate | CA-signed (Let's Encrypt), auto-renewed |
| Single thread, no client certs | Thread pool, HSTS header, HTTP→HTTPS redirect |
| Trust only via import into the local trust store | Verification against system trust store, OCSP staple |
| Only server authenticated | if needed: mutual TLS (mTLS) for client authentication |

> **Conclusion:** TLS = confidentiality (AES-GCM) + integrity (AEAD tag) + authentication (certificate) + forward secrecy (ephemeral key exchange). Integration into an app: an SSL context, a certificate, a wrapped socket. The certificate from mission 7 provides the identity, TLS protects what leaves the application.