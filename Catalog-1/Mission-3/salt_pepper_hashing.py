"""
Mission-3: Password hashing with salting (and optional peppering).

Demonstrates:
  1. Insecure vs. salted hashing, why identical passwords must not look identical.
  2. Per-password random salt + slow KDF (scrypt, from the Python stdlib).
  3. Optional pepper: a *secret* value NOT stored in the password database.
  4. Constant-time verification (hmac.compare_digest) to avoid timing leaks.

Run:
    python salt_pepper_hashing.py
    python salt_pepper_hashing.py --pepper super-secret-42
"""

import base64
import hashlib
import hmac
import os
import secrets

# KDF parameters — tune per deployment; values here are for demo purposes.
SCRYPT_N = 2 ** 14   # CPU/memory cost
SCRYPT_R = 8         # block size
SCRYPT_P = 1         # parallelization
SALT_BYTES = 16


def derive(password: str, salt: bytes, pepper: str = "") -> bytes:
    """Key derivation: scrypt(salt || password || pepper), 32-byte output.

    Salt:     random, per-password, stored in plaintext next to the hash.
    Pepper:   global secret, NOT stored with the hashes (env var / vault).
    """
    material = password.encode("utf-8")
    if pepper:
        # HMAC construction: pepper as key keeps the secret separate
        # even if the KDF output is ever truncated or mangled.
        mac = hmac.new(pepper.encode("utf-8"), salt + material, hashlib.sha256)
        material = mac.digest()
    return hashlib.scrypt(
        material,
        salt=salt,
        n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P,
        dklen=32,
    )


def hash_password(password: str, pepper: str = "") -> str:
    """Format: scrypt$n$r$p$base64(salt)$base64(hash), everything needed
    for verification except (hopefully) the pepper."""
    salt = secrets.token_bytes(SALT_BYTES)
    digest = derive(password, salt, pepper)
    return "scrypt$%d$%d$%d$%s$%s" % (
        SCRYPT_N, SCRYPT_R, SCRYPT_P,
        base64.b64encode(salt).decode(),
        base64.b64encode(digest).decode(),
    )


def verify_password(stored: str, password: str, pepper: str = "") -> bool:
    """Recompute with the stored salt and compare in constant time."""
    try:
        algo, n, r, p, salt_b64, hash_b64 = stored.split("$")
        if algo != "scrypt":
            return False
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
        actual = derive(password, salt, pepper)
        return hmac.compare_digest(expected, actual)
    except (ValueError, TypeError):
        return False  # malformed record — never raise


def naive_hash(password: str) -> str:
    """Bad practice on purpose: plain fast hash, no salt. Rainbow tables
    and cross-user duplicate detection work against exactly this."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def demo(pepper: str = ""):
    users: dict[str, str] = {}  # stands in for the password database
    alice_pw = bob_pw = "CorrectHorse!"  # same password on purpose

    for name, pw in (("alice", alice_pw), ("bob", bob_pw), ("mallory", "hunter2")):
        users[name] = hash_password(pw, pepper)

    print(f"Pepper in use: {'yes' if pepper else 'no'}")
    print("\n--- Naive (unsalted) hashes ---")
    for pw in (alice_pw, bob_pw):
        print(f"  {pw:<15} {naive_hash(pw)}")
    print("  -> identical hash for identical password: leaks a shared password,")
    print("     and one rainbow table covers the whole database.")

    print("\n--- Salted + peppered storage ---")
    for name, rec in users.items():
        print(f"  {name:<8} {rec}")

    print("\n--- Verification ---")
    for name in users:
        ok = verify_password(users[name], alice_pw, pepper)
        print(f"  {name} + 'CorrectHorse!': {'valid' if ok else 'invalid'}")

    bad = verify_password(users["alice"], "WrongPassword!", pepper)
    print(f"  alice + 'WrongPassword!': {'valid' if bad else 'invalid'}")

    # Attacker stole the DB but not the pepper:
    if pepper:
        ok = verify_password(users["alice"], "CorrectHorse!", pepper="")
        print(f"  DB-only leak, cracked with wrong (missing) pepper: "
              f"{'valid' if ok else 'invalid (hashes useless)'}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pepper", help="secret pepper (in practice: env var or vault, not argv)")
    parser.add_argument("-e", "--pepper-env", default="PASSWORD_PEPPER",
                        help="env variable that holds the pepper")
    args = parser.parse_args()

    pepper = args.pepper or os.environ.get(args.pepper_env, "")
    demo(pepper)