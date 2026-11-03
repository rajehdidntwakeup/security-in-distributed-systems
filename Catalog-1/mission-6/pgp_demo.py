"""
PGP demo with Python (python-gnupg library on top of GnuPG).

Shows the complete cycle:
  1. key pair generation
  2. signing a message
  3. encrypting with the public key
  4. decrypting with the private key
  5. sign & encrypt in one step
  6. verifying a signature - and detecting tampering

Hybrid scheme in the background: the message is encrypted with AES
(symmetric), the random session key with Alice's RSA public key.

Requires: pip install python-gnupg  and  GnuPG (gpg) available.
Uses a temporary keyring, so it is repeatable and touches nothing else.
"""

import os
import shutil
import tempfile

import gnupg

ALICE = "alice@example.com"


def find_gpg() -> str:
    """Locate a gpg binary, also when it is not on the PATH
    (git-bash gpg, Gpg4win) and also in cmd/PowerShell windows."""
    common = [
        shutil.which("gpg"),
        r"C:\Program Files\Git\usr\bin\gpg.exe",
        r"C:\Program Files (x86)\Git\usr\bin\gpg.exe",
        r"C:\Program Files (x86)\GnuPG\bin\gpg.exe",
        r"C:\Program Files\GnuPG\bin\gpg.exe",
    ]
    for path in common:
        if path and os.path.isfile(path):
            return path
    raise SystemExit("gpg not found - install GnuPG (Gpg4win) or Git for Windows.")


def rule(title: str) -> None:
    print("\n" + "=" * 50)
    print(f" {title}")
    print("=" * 50)


def main() -> None:
    gpgbinary = find_gpg()
    # Temp keyring -> demo is repeatable and leaves no traces
    with tempfile.TemporaryDirectory() as home:
        if r"\Git\usr\bin" in gpgbinary or "/Git/" in gpgbinary.replace("\\", "/"):
            # Git's GnuPG is an MSYS build and needs a POSIX-style GNUPGHOME:
            os.environ["GNUPGHOME"] = "/c/" + home[3:].replace("\\", "/")
        else:
            # native Gpg4win build: normal Windows path
            os.environ["GNUPGHOME"] = home
        print(f"gpg binary: {gpgbinary}")
        gpg = gnupg.GPG(gpgbinary=gpgbinary)

        rule("1. Generate key pair (RSA-2048, no passphrase)")
        key = gpg.gen_key(gpg.gen_key_input(
            name_real="Alice",
            name_email=ALICE,
            key_type="RSA",
            key_length=2048,
            no_protection=True,
        ))
        print(f"Fingerprint: {key.fingerprint}")

        rule("2. Sign a message (authenticity + integrity)")
        message = "Hello from Alice - this message is signed, not encrypted."
        signed = gpg.sign(message, keyid=ALICE, clearsign=True)
        print("--- signed message (armored): ---")
        print(signed.data.decode())

        rule("3. Encrypt a message for Alice (confidentiality)")
        print("    -> uses her PUBLIC key; session key is AES (hybrid)")
        secret = "Top secret meeting notes."
        encrypted = gpg.encrypt(secret, recipients=ALICE, armor=True)
        print(f"plaintext length : {len(secret)} chars")
        print(f"ciphertext length: {len(str(encrypted))} chars")
        print("--- ciphertext, first lines: ---")
        print("\n".join(str(encrypted).splitlines()[:3]) + "\n...")

        rule("4. Decrypt (Alice uses her PRIVATE key)")
        decrypted = gpg.decrypt(str(encrypted))
        print(f"decrypted: {decrypted.data.decode()!r}  ok={decrypted.ok}")

        rule("5. Sign AND encrypt in one step")
        sealed = gpg.encrypt(secret, recipients=ALICE, sign=ALICE)
        reopened = gpg.decrypt(str(sealed))
        print(f"decrypted: {reopened.data.decode()!r}")
        print(f"signature valid: {reopened.valid}  signed by: {reopened.username}")

        rule("6. Verify a signature - and detect tampering")
        check = gpg.verify(signed.data)
        print(f"original  -> valid={check.valid}, signer={check.username}")

        # A forger edits the message body but keeps the signature block:
        forged = signed.data.replace(b"Hello from Alice", b"Hello from Bob!!")
        check2 = gpg.verify(forged)
        print(f"tampered  -> valid={check2.valid}  (must be False)")

        rule("Demo complete")


if __name__ == "__main__":
    main()