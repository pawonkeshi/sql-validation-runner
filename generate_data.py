"""Generate sample source/target order data with deliberate defects.

Defects planted in target:
  - 5 missing rows
  - 3 duplicate order_ids
  - 4 null customer_ids
  - 2 wrong amounts
"""
import random
from pathlib import Path

import pandas as pd

SEED = 42
N_ROWS = 1000
DATA_DIR = Path("data")


def build_source(n: int) -> pd.DataFrame:
    rng = random.Random(SEED)
    statuses = ["NEW", "SHIPPED", "DELIVERED", "CANCELLED"]
    rows = []
    for i in range(1, n + 1):
        rows.append({
            "order_id": i,
            "customer_id": rng.randint(1000, 1999),
            "order_date": pd.Timestamp("2026-01-01") + pd.Timedelta(days=rng.randint(0, 300)),
            "amount": round(rng.uniform(10, 500), 2),
            "status": rng.choice(statuses),
        })
    return pd.DataFrame(rows)


def build_target(source: pd.DataFrame) -> pd.DataFrame:
    rng = random.Random(SEED + 1)
    target = source.copy()

    # Pick 14 distinct rows so defects never overlap: 5 + 3 + 4 + 2
    picks = rng.sample(list(target.index), 14)
    missing, dupes, nulls, wrong = picks[:5], picks[5:8], picks[8:12], picks[12:14]

    target.loc[nulls, "customer_id"] = None
    target.loc[wrong, "amount"] = target.loc[wrong, "amount"] + 25.00
    duplicate_rows = target.loc[dupes]
    target = target.drop(index=missing)
    target = pd.concat([target, duplicate_rows], ignore_index=True)

    print("Planted defects:")
    print(f"  missing order_ids:   {sorted(source.loc[missing, 'order_id'].tolist())}")
    print(f"  duplicate order_ids: {sorted(source.loc[dupes, 'order_id'].tolist())}")
    print(f"  null customer_id on: {sorted(source.loc[nulls, 'order_id'].tolist())}")
    print(f"  wrong amount on:     {sorted(source.loc[wrong, 'order_id'].tolist())}")
    return target


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    source = build_source(N_ROWS)
    target = build_target(source)
    source.to_csv(DATA_DIR / "source_orders.csv", index=False)
    target.to_csv(DATA_DIR / "target_orders.csv", index=False)
    print(f"\nWrote {len(source)} source rows and {len(target)} target rows to {DATA_DIR}/")


if __name__ == "__main__":
    main()