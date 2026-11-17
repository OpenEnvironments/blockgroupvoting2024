"""Combine the per-state block group outputs into one file.

Usage: python src/combine_outputs.py [--in-dir data/interim/states] [--out data/processed/blockgroupvoting2024.csv]
Reads every {st}_blockgroup_votes.csv, checks the 50 states and DC are all present, and writes one CSV
with the same columns, ordered by STATE then BLOCKGROUP_GEOID.
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

from load import STATE_FIPS
from run_state import OUTPUT_COLUMNS


def combine(in_dir):
    """All per-state outputs in `in_dir` as one DataFrame. Raises if a state is missing or duplicated."""
    files = sorted(Path(in_dir).glob("??_blockgroup_votes.csv"))
    frames = [pd.read_csv(f, dtype={"BLOCKGROUP_GEOID": str}) for f in files]
    missing = sorted(set(STATE_FIPS) - {f.name[:2].upper() for f in files})
    if missing:
        raise FileNotFoundError(f"no output for: {', '.join(missing)}")
    out = pd.concat(frames, ignore_index=True)[OUTPUT_COLUMNS]
    if out["BLOCKGROUP_GEOID"].duplicated().any():
        raise ValueError("BLOCKGROUP_GEOID is not unique across states")
    return out.sort_values(["STATE", "BLOCKGROUP_GEOID"], ignore_index=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--in-dir", default="data/interim/states")
    ap.add_argument("--out", default="data/processed/blockgroupvoting2024.csv")
    args = ap.parse_args(argv)
    out = combine(args.in_dir)
    out.to_csv(args.out, index=False)
    print(f"wrote {len(out)} block groups, {out['TOT'].sum():,.0f} votes -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
