"""Allocate each state's 2024 precinct presidential votes onto block groups.

Usage: python src/run_state.py --states RI VT
       python src/run_state.py --fec-ok      # every state whose totals pass the FEC check
Writes data/processed/{st}_blockgroup_votes.csv with columns REP, DEM, OTH, STATE, BLOCKGROUP_GEOID.
"""

import argparse
import sys
import time
from pathlib import Path

from allocate import EQUAL_AREA_CRS as DEFAULT_CRS
from allocate import allocate_votes
from check_totals import FEC_NAME
from ingest import VOTE_KEYS, check_state_totals
from load import EQUAL_AREA_CRS, find_block_groups, load_block_groups, load_precincts


OUTPUT_COLUMNS = ["REP", "DEM", "OTH", "STATE", "BLOCKGROUP_GEOID"]


def format_output(allocated, state):
    """Rename the allocated vote columns to the delivered layout, one row per block group."""
    out = allocated[["rep", "dem", "other"]].rename(columns={"rep": "REP", "dem": "DEM", "other": "OTH"})
    out["STATE"] = state.upper()
    out.index.name = "BLOCKGROUP_GEOID"
    return out.reset_index()[OUTPUT_COLUMNS]


def run_state(raw_dir, out_dir, state):
    """Allocate one state; returns a summary dict. Raises if votes are not conserved."""
    bg_file = find_block_groups(raw_dir, state).name  # fail early, before the slow precinct read
    precincts = load_precincts(raw_dir, state)
    block_groups = load_block_groups(raw_dir, state)
    allocated, unallocated = allocate_votes(
        precincts,
        block_groups,
        VOTE_KEYS,
        bg_id="GEOID",
        land_fraction_col="land_fraction",
        crs=EQUAL_AREA_CRS.get(state, DEFAULT_CRS),
    )
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    format_output(allocated, state).to_csv(out_dir / f"{state.lower()}_blockgroup_votes.csv", index=False)
    lost = precincts.loc[precincts["precinct_id"].isin(unallocated), VOTE_KEYS].sum().sum()
    return {
        "block_group_file": bg_file,
        "precincts": len(precincts),
        "block_groups": len(allocated),
        "precinct_total": float(precincts[VOTE_KEYS].sum().sum()),
        "allocated_total": float(allocated[VOTE_KEYS].sum().sum()),
        "unallocated_precincts": len(unallocated),
        "unallocated_votes": float(lost),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw-dir", default="data/raw")
    ap.add_argument("--out-dir", default="data/processed")
    ap.add_argument("--states", nargs="*", default=[])
    ap.add_argument("--fec-ok", action="store_true", help="run only states that pass the FEC totals check")
    ap.add_argument("--max-pct-diff", type=float, default=0.001)
    ap.add_argument(
        "--fec-columns", nargs="*", default=["dem", "rep"], choices=["dem", "rep", "other", "total"],
        help="columns judged by --fec-ok (default: Harris and Trump only)",
    )
    args = ap.parse_args(argv)

    states = [s.upper() for s in args.states]
    if args.fec_ok:
        fec_path = Path(args.raw_dir) / "fec" / FEC_NAME
        comparison, _ = check_state_totals(args.raw_dir, fec_path, None, args.max_pct_diff, args.fec_columns)
        states += [s for s in comparison.index[comparison["ok"]] if s not in states]
    if not states:
        ap.error("give --states and/or --fec-ok")

    failures, skipped = [], []
    for st in states:
        start = time.time()
        try:
            s = run_state(args.raw_dir, args.out_dir, st)
        except FileNotFoundError as e:  # input missing: leave any existing output untouched
            skipped.append(st)
            print(f"{st}: SKIPPED {e}", flush=True)
            continue
        except Exception as e:  # keep going so one bad state doesn't hide the rest
            failures.append(st)
            print(f"{st}: FAILED {type(e).__name__}: {e}", flush=True)
            continue
        print(
            f"{st}: {s['precincts']} precincts -> {s['block_groups']} block groups ({s['block_group_file']}), "
            f"votes {s['precinct_total']:,.0f} in / {s['allocated_total']:,.0f} out, "
            f"{s['unallocated_precincts']} unallocated precincts ({s['unallocated_votes']:,.0f} votes), "
            f"{time.time() - start:.0f}s",
            flush=True,
        )
    if skipped:
        print(f"skipped (input missing, existing output left as is): {', '.join(skipped)}", flush=True)
    return 1 if failures or skipped else 0


if __name__ == "__main__":
    sys.exit(main())
