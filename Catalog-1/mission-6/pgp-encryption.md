# PGP (Pretty Good Privacy)

## What is PGP?

**PGP** (Pretty Good Privacy, Phil Zimmermann, 1991) is a program/standard for
**encrypted and signed communication**. Its data format lives on today as
**OpenPGP** (RFC 4880); the widespread open-source implementation is
**GnuPG (GPG)**: in practice "PGP" and "GPG" are used interchangeably.

## How PGP works: hybrid encryption

PGP is **both**: it is not a single cipher, but a clever combination of
symmetric and asymmetric encryption ("hybrid"):

1. **Symmetric encryption of the message**: the (possibly large) message is
   encrypted with a fresh, random **session key** using a fast cipher
   (e.g. AES-128/256).
2. **Asymmetric encryption of the session key**: this one-off session key is
   encrypted with the **recipient's public key** (RSA or ECC) and attached to
   the ciphertext.
3. **Decryption**: the recipient's private key (RSA/ECC) unlocks only the
   session key, which then decrypts the actual message fast.

So each message needs only a small RSA operation (~2 lines of math per KB),
and the heavy lifting is done by fast symmetric encryption. RSA alone cannot
encrypt large files, PGP can.

### Authenticity: signatures

PGP encrypts data *and* makes it **authentic**. To sign, a **hash** (SHA-256)
of the message is computed and encrypted with the **signer's private key**.
Anyone with the public key can verify: hash the received message yourself and
compare. This guarantees **integrity** (message unchanged) and **authenticity**
(message really comes from the key holder). Signing and encrypting can be
combined ("sign & encrypt").

### The web of trust

Instead of a central certificate authority (as in TLS/PKI), PGP users
**sign each other's public keys**. If I trust a friend's key, and they have
verified Alice's identity, I can extend partial trust to Alice's key;
trust propagates through a decentralized **web of trust**. In practice most
people today verify key **fingerprints** directly (in person or per video call)
instead.

## Symmetric vs. asymmetric: how they differ in practice

| | **Symmetric (AES)** | **PGP / OpenPGP (hybrid)** |
|---|---|---|
| Keys | One shared secret key for both parties | Key pair: public + private; each participant owns their own |
| Key exchange | Hard: secret key must reach the partner over a confidential channel beforehand | Easy: the public key is published/shared openly, no secret transport |
| Speed | Very fast, any data size | Slower per operation, but only the session key is asymmetrically encrypted |
| Participants | n people need n·(n−1)/2 different pairwise keys | n people each manage exactly 1 key pair |
| Scope of use | Session-based channel encryption without identity/keys between peers: disk encryption, VPN, Wi-Fi (WPA2), TLS bulk traffic, databases | **Object-based** end-to-end encryption of files, e-mails, text messages between identified persons, plus signatures |
| Identity/integrity | None by itself: AES alone cannot prove *who* sent something | Built in: every message can be signed |
| Trust model | Presupposes pre-shared secret or PKI | Web of trust / fingerprint verification, no central authority |

**Application pattern**: this is the practical difference:

- **Symmetric** is used when both sides already share a secret channel or the
  context provides one: full-disk encryption, database encryption, TLS
  session data, file safe with one password.
- **PGP** is used when **strangers want to communicate securely without prior
  agreement between participants**: you can encrypt an e-mail for someone
  you have never met, using only their published public key, and they alone
  can read it.

## Typical areas of use

- **E-mail encryption**: the classic use case (e.g. Enigmail, Thunderbird
  plug-ins): end-to-end encryption so that even the e-mail provider cannot
  read messages.
- **Signed e-mail**: prove an e-mail genuinely comes from the sender
  (protection against phishing/spoofing).
- **Secure file exchange**: encrypt files/archives before sending
  (e.g. to a business partner, lawyer, journalist).
- **Full-disk / partition encryption**: GnuPG-based disk keys (some
  distributions store LUKS recovery data PGP-encrypted).
- **Software distribution**: signing releases/installers/packages so users
  can verify authenticity (Linux package repositories, git commit signing).
- **Password managers and backups**: encrypt secret stores with one key pair.
- **Whistleblower systems**: SecureDrop journalists publish PGP keys so
  anonymous sources can encrypt to them.

## Advantages in practice

- **Solves the key distribution problem**: no secret ever needs to be
  transmitted.
- **End-to-end security without infrastructure**: no key server, no CA, no
  provider needs to participate or be trusted.
- **Confidentiality + authenticity + integrity** in one scheme.
- **Scalable**: one key pair per person, not one key per partner pair.
- **Fast** thanks to the hybrid design.
- **Open standard** (OpenPGP) with free implementations (GnuPG) and broad
  tooling.

## Demo

`pgp_demo.py` builds a fresh key pair in a temporary keyring and shows the
complete cycle: **key generation → signing → encryption → sign & encrypt →
decryption → signature verification**. It uses the `python-gnupg` library
(`pip install python-gnupg`) on top of GnuPG; run it with `python pgp_demo.py`.
Raw output of the run: `python-demo-output.txt`.