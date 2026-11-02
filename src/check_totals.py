"""Check that each state's 2024 precinct results total the FEC results.

Usage: python src/check_totals.py [--raw-dir data/raw] [--states AZ TX ...] [--max-pct-diff 0.001]
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

from ingest import check_state_totals

FEC_NAME = "Federal Election Commission, Official 2024 Presidential General Election Results.csv"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw-dir", default="data/raw")
    ap.add_argument("--fec-file", default=None, help="defaults to the FEC CSV in <raw-dir>/fec")
    ap.add_argument("--states", nargs="*")
    ap.add_argument("--max-pct-diff", type=float, default=0.001, help="allowed fractional difference")
    ap.add_argument(
        "--columns", nargs="*", choices=["dem", "rep", "other", "total"],
        help="columns to judge (default all); e.g. --columns dem rep ignores all other candidates",
    )
    args = ap.parse_args(argv)

    fec_path = Path(args.fec_file) if args.fec_file else Path(args.raw_dir) / "fec" / FEC_NAME
    comparison, missing = check_state_totals(args.raw_dir, fec_path, args.states, args.max_pct_diff, args.columns)

    if not comparison.empty:
        show = comparison[["dem_diff", "rep_diff", "other_diff", "total_diff", "max_pct_diff", "ok"]]
        with pd.option_context("display.float_format", "{:,.4f}".format, "display.width", 200):
            print(show.to_string())
    failed = comparison.index[~comparison["ok"]].tolist() if not comparison.empty else []
    print(f"\nchecked {len(comparison)} states: {len(comparison) - len(failed)} ok, {len(failed)} outside tolerance")
    if failed:
        print("outside tolerance:", ", ".join(failed))
    if missing:
        print("no 2024 general results file (not checked):", ", ".join(missing))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
