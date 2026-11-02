"""
Scenario:
1. "Sender" computes the SHA-256 digest of a message and sends
   the message + digest to the "receiver".
2. Message gets (optionally) tampered with in transit.
3. "Receiver" recomputes the digest and compares it to the one received.
   - Match  -> data intact
   - Mismatch -> data was modified (corruption or tampering)

Run:  python verify_integrity.py
"""

import hashlib

# --- Step 1: Sender creates a message -----------------------------------
original_message = (
    b"Transfer: 1,000 coins from Alice to Bob.\n"
    b"Reference: 2026-11-02 / INV-42\n"
)

# --- Step 2: Sender computes the SHA-256 digest --------------------------
def sha256_digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

sent_digest = sha256_digest(original_message)
print("Sender's digest :", sent_digest)

# --- Step 3: Message travels over the network ----------------------------
TAMPER = False  # set to False to see the "intact" case

if TAMPER:
    received_message = original_message.replace(b"Alice", b"Eve")
    print("Tampered in transit: Alice -> Eve")
else:
    received_message = original_message

# --- Step 4: Receiver recomputes the digest ------------------------------
computed_digest = sha256_digest(received_message)
print("Receiver's digest:", computed_digest)

# --- Step 5: Compare -------------------------------------------------------
if computed_digest == sent_digest:
    print("RESULT: INTEGRITY OK - message unchanged.")
else:
    print("RESULT: INTEGRITY FAILED - message was modified!")
    print("Even one changed character completely changes the digest (avalanche effect).")
