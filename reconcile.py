#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""

import json
from decimal import Decimal
from datetime import datetime

latest_attempts = {}

with open("payments.jsonl", encoding="utf-8") as file:
    for line in file:
        try:
            event = json.loads(line)

            txn_id = event.get("txn_id")
            if not txn_id:
                continue

            timestamp = datetime.fromisoformat(
                event["ts"].replace("Z", "+00:00")
            )

            previous = latest_attempts.get(txn_id)

            if previous is None or timestamp > previous[0]:
                latest_attempts[txn_id] = (timestamp, event)

        except (json.JSONDecodeError, KeyError, ValueError, TypeError):
            continue

total = Decimal("0")
count = 0

for timestamp, event in latest_attempts.values():
    if event["status"] == "success":
        amount = Decimal(str(event["amount"]).replace(",", ""))
        total += amount
        count += 1

with open("expected.txt", encoding="utf-8") as file:
    expected = int(file.read().strip())

if count != expected:
    print(
        f"Check failed: counted {count} successful payments, "
        f"expected {expected}."
    )
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
