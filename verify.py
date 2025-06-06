#!/usr/bin/env python3
"""verify.py  –  Provably-fair verification tool for GameRoll rounds.

Usage example:
    python scripts/verify.py \
        --seed  e3c0...   \
        --hash  f12a...   \
        --bets  bets.json

The script validates that:
1. SHA-256(seed) equals committed hash published before the round.
2. Using the same ticket algorithm the winner calculated locally matches the server.

See scripts/README.md for full documentation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from decimal import Decimal, ROUND_HALF_UP, getcontext
from pathlib import Path
from typing import Dict, List, Tuple

# Configure Decimal: 28 digits precision is enough for any realistic pool
getcontext().prec = 28
CENT = Decimal("0.01")  # one ticket = 0.01 TON (1 «cent»)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_bets(path: Path) -> Tuple[Dict[str, Decimal], Dict[str, str]]:
    """Load JSON mapping.

    Accepted formats:
        {"123": 3.0, "456": 7.21}
        {"123": {"amount": 3.0, "username": "alice"}, ...}

    Returns two dicts:
        amounts – {user_id: Decimal}
        usernames – {user_id: username or ""}
    """
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        sys.exit(f"Failed to read bets file '{path}': {exc}")

    if not isinstance(raw, dict):
        sys.exit("bets.json must be a JSON object like {\"alice\": 1.23, ...}")

    bets: Dict[str, Decimal] = {}
    usernames: Dict[str, str] = {}

    for user, amount in raw.items():
        if isinstance(amount, dict):
            amt_val = amount.get("amount")
            username_val = amount.get("username") or ""
        else:
            amt_val = amount
            username_val = ""

        try:
            dec = Decimal(str(amt_val)).quantize(CENT, ROUND_HALF_UP)
        except Exception:
            sys.exit(f"Stake '{amt_val}' for user '{user}' is not a valid number")
        if dec <= 0:
            sys.exit(f"Stake for user '{user}' must be positive")
        bets[user] = bets.get(user, Decimal()) + dec
        if username_val:
            usernames[user] = username_val

    return bets, usernames


def cents_map(bets: Dict[str, Decimal]) -> List[Tuple[str, int]]:
    """Convert amounts to integer tickets (cents) and sort by user_id (asc)."""
    return sorted([(u, int((amt / CENT).to_integral_value())) for u, amt in bets.items()])


def pick_winner(bets_cents: List[Tuple[str, int]], seed_bytes: bytes) -> Tuple[str, int]:
    """Return (winner_user_id, picked_ticket_index)."""
    total = sum(c for _, c in bets_cents)
    if total == 0:
        sys.exit("The round contains no tickets – nothing to verify")

    rand_int = int.from_bytes(hashlib.sha256(seed_bytes).digest(), "big")
    index = rand_int % total

    acc = 0
    for user, cents in bets_cents:
        acc += cents
        if index < acc:
            return user, index

    # Should never reach here if algorithm correct
    raise RuntimeError("Winner could not be determined (internal error)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Verify provably-fair GameRoll round")
    parser.add_argument("--seed", required=True, help="64-char hex string revealed after the round")
    parser.add_argument("--hash", required=True, help="64-char hex SHA-256 published before the round")
    parser.add_argument("--bets", required=True, type=Path, help="Path to bets.json exported from the round")
    args = parser.parse_args()

    # 1. Validate seed ↔ hash
    if len(args.seed) != 64:
        sys.exit("Seed must be 64 hex characters (32 bytes)")
    try:
        seed_bytes = bytes.fromhex(args.seed)
    except ValueError:
        sys.exit("Seed is not valid hexadecimal data")

    calc_hash = hashlib.sha256(seed_bytes).hexdigest()
    if calc_hash.lower() != args.hash.lower():
        sys.exit("❌  HASH mismatch – seed has been tampered with")

    # 2. Read bets file
    bets, usernames = load_bets(args.bets)
    bets_cents = cents_map(bets)

    # 3. Pick winner using the same algorithm as the server
    winner, ticket = pick_winner(bets_cents, seed_bytes)

    total_tickets = sum(c for _, c in bets_cents)

    # 4. Output result
    print("✅  Round verified as provably fair!")
    print(f"Hash   : {args.hash}")
    print(f"Seed   : {args.seed}")
    print(f"Bets   : {args.bets} ({len(bets)} players, {total_tickets} tickets)")
    winner_username = usernames.get(winner, "")
    if winner_username:
        print(f"Winner : {winner} (@{winner_username})")
    else:
        print(f"Winner : {winner}")
    print(f"Ticket : {ticket} (range 0…{total_tickets - 1})")


if __name__ == "__main__":
    main() 
