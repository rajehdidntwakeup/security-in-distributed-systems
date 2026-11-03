"""Mission-3: password hashing with salting (and optional peppering).

Run:
    python salt_pepper_hashing.py
    python salt_pepper_hashing.py super-secret-42   # optional pepper

Note: plain SHA-256 is used to keep the demo simple.
In production use a slow hash like Argon2id, scrypt or bcrypt.
"""

import hashlib
import secrets


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def hash_password(password: str, salt: str, pepper: str = "") -> str:
    """Salt is stored NEXT TO the hash; pepper is a secret kept outside the DB."""
    return f"{salt}${sha256(f'{salt}|{password}|{pepper}')}"


def check_password(stored: str, password: str, pepper: str = "") -> bool:
    """Recompute the hash with the stored salt and compare."""
    salt, expected = stored.split("$")
    return sha256(f"{salt}|{password}|{pepper}") == expected


if __name__ == "__main__":
    import sys

    pepper = sys.argv[1] if len(sys.argv) > 1 else ""
    if pepper:
        print("Pepper in use:", pepper)

    password = "hunter2"

    # 1) Unsalted: same password -> identical hash (rainbow table friendly!)
    print("Unsalted      :", sha256(password))
    print("Unsalted again:", sha256(password))

    # 2) Salted (+ peppered): new random salt on every call
    alice = hash_password(password, secrets.token_hex(8), pepper)
    bob = hash_password(password, secrets.token_hex(8), pepper)
    print("Alice's       :", alice)
    print("Bob's         :", bob)

    # 3) Verification
    print("check Alice + 'hunter2' ->", check_password(alice, password, pepper))  # True
    print("check Alice + 'hunter3' ->", check_password(alice, "hunter3", pepper))  # False