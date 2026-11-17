"""Combine every state's 2024 precinct polygons and votes (RDH, plus NYT for DC) into one file.

Usage: python src/export_precincts.py [--states AK AL ...] [--out data/interim/precincts_2024.gpkg]
Writes a GeoPackage (layer `precincts`, EPSG:4326) with PRECINCT_ID, STATE, SOURCE, REP, DEM, OTH, TOT.
Geometries are exactly as published (not repaired); no block group data is involved.
"""

import argparse
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

from load import STATE_FIPS, load_precincts
from nyt import NYT_STATES

OUT_CRS = "EPSG:4326"
COLUMNS = ["PRECINCT_ID", "STATE", "SOURCE", "REP", "DEM", "OTH", "TOT", "geometry"]


def state_precincts(raw_dir, state):
    """One state's precincts in the delivered layout and CRS."""
    p = load_precincts(raw_dir, state).to_crs(OUT_CRS)
    out = gpd.GeoDataFrame(
        {
            "PRECINCT_ID": p["precinct_id"],
            "STATE": state.upper(),
            "SOURCE": "NYT" if state.upper() in NYT_STATES else "RDH",
            "REP": p["rep"],
            "DEM": p["dem"],
            "OTH": p["other"],
        },
        geometry=p.geometry,
        crs=OUT_CRS,
    )
    out["TOT"] = out["REP"] + out["DEM"] + out["OTH"]
    return out[COLUMNS]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw-dir", default="data/raw")
    ap.add_argument("--out", default="data/interim/precincts_2024.gpkg")
    ap.add_argument("--states", nargs="*", default=list(STATE_FIPS))
    args = ap.parse_args(argv)

    frames = []
    for st in (s.upper() for s in args.states):
        frames.append(state_precincts(args.raw_dir, st))
        print(f"{st}: {len(frames[-1])} precincts, {frames[-1]['TOT'].sum():,.0f} votes", flush=True)
    allp = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), geometry="geometry", crs=OUT_CRS)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    allp.to_file(out, layer="precincts", driver="GPKG")
    print(f"wrote {len(allp)} precincts, {allp['TOT'].sum():,.0f} votes -> {out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
