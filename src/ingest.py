"""Ingest RDH 2024 presidential results and FEC state totals, and compare them."""

import re
import zipfile
from pathlib import Path

import pandas as pd
import pyogrio

from nyt import NYT_STATES, nyt_vote_totals

DEM, REP = "G24PREDHAR", "G24PRERTRU"
WI_DEM, WI_REP = "PREDEM24", "PREREP24"
VOTE_KEYS = ["dem", "rep", "other"]
GEO_EXTS = (".shp", ".geojson", ".gpkg")


def load_fec(path):
    """Read the FEC state totals; returns one row per state (upper-case abbreviation)."""
    raw = pd.read_csv(path, encoding="utf-8-sig", thousands=",")
    raw.columns = ["state", "dem", "rep", "other"]
    raw["state"] = raw["state"].str.strip()
    us_total = raw[raw["state"].str.lower().str.startswith("u.s.")]
    fec = raw.drop(us_total.index).set_index("state")
    if len(us_total) == 1:
        diff = fec[VOTE_KEYS].sum() - us_total.iloc[0][VOTE_KEYS].astype(float)
        if (diff != 0).any():
            raise ValueError(f"FEC state rows do not sum to the U.S. total row: {diff.to_dict()}")
    fec["total"] = fec[VOTE_KEYS].sum(axis=1)
    return fec


def classify_presidential_columns(columns):
    """Split a state's columns into Harris (dem), Trump (rep) and all other presidential votes."""
    cols = list(columns)
    if DEM in cols and REP in cols:
        pres = [c for c in cols if c.startswith("G24PRE")]
        dem, rep = [DEM], [REP]
    elif WI_DEM in cols and WI_REP in cols:
        # PRETOT24 is a statewide total across candidates, not a candidate
        pres = [c for c in cols if re.fullmatch(r"PRE[A-Z]{3}24|PRENP\d24", c) and c != "PRETOT24"]
        dem, rep = [WI_DEM], [WI_REP]
    else:
        raise ValueError("no recognised presidential vote columns")
    return {"dem": dem, "rep": rep, "other": [c for c in pres if c not in dem + rep]}


def find_precinct_results(raw_dir, state):
    """Path to the state's 2024 general precinct zip, or None.

    Matches `{st}_2024_gen_*.zip` (e.g. `ak_2024_gen_prec.zip`, `tx_2024_gen_tx_vtd.zip`),
    ignoring block-level disaggregations, and prefers the `_prec` file.
    """
    found = sorted(
        p for p in (Path(raw_dir) / "rdh").glob(f"{state.lower()}_2024_gen_*.zip") if "blocks" not in p.name
    )
    if not found:
        return None
    preferred = [p for p in found if p.name.endswith("_prec.zip")]
    if len(preferred) == 1:
        return preferred[0]
    if len(found) == 1:
        return found[0]
    raise ValueError(f"cannot pick a single results file for {state}: {[p.name for p in found]}")


def pick_layer(zip_path):
    """Name of the statewide results layer inside a precinct zip.

    Some zips hold several layers (all, cong, sldl, sldu); the `_all_` layer
    has the statewide results. A zip with one layer needs no such choice.
    """
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
    layers = [n for n in names if n.lower().endswith(GEO_EXTS)]
    if len(layers) > 1:
        layers = [n for n in layers if "_all_" in Path(n).name]
    if len(layers) != 1:
        raise ValueError(f"cannot pick a single results layer in {zip_path}")
    return layers[0]


def _read_vote_table(zip_path, wanted):
    """Read only the classified vote columns (no geometry) from a precinct zip."""
    df = pyogrio.read_dataframe(f"zip://{zip_path}!{pick_layer(zip_path)}", read_geometry=False)
    groups = wanted(df.columns)
    return df[sum(groups.values(), [])], groups


def state_vote_totals(zip_path):
    """Sum a state's presidential votes into dem, rep, other and total."""
    table, groups = _read_vote_table(zip_path, classify_presidential_columns)
    totals = {key: float(table[cols].sum().sum()) for key, cols in groups.items()}
    totals["total"] = sum(totals.values())
    return totals


def compare_to_fec(precinct_totals, fec, max_pct_diff=0.001, columns=None):
    """Compare per-state totals (DataFrame: dem, rep, other, total) with the FEC.

    A state is ok when every judged column differs from the FEC by at most
    `max_pct_diff` (a fraction of the FEC value). `columns` limits which of
    dem, rep, other, total are judged (default all); the rest are still shown.
    """
    cols = VOTE_KEYS + ["total"]
    judged = list(columns) if columns else cols
    out = pd.DataFrame(index=precinct_totals.index)
    for c in cols:
        out[f"{c}_precinct"] = precinct_totals[c]
        out[f"{c}_fec"] = fec.loc[out.index, c]
        out[f"{c}_diff"] = out[f"{c}_precinct"] - out[f"{c}_fec"]
    pct = pd.concat([(out[f"{c}_diff"].abs() / out[f"{c}_fec"]) for c in judged], axis=1)
    out["max_pct_diff"] = pct.max(axis=1)
    out["ok"] = out["max_pct_diff"] <= max_pct_diff
    return out


def check_state_totals(raw_dir, fec_path, states=None, max_pct_diff=0.001, columns=None):
    """Check each state's precinct-level votes against the FEC.

    Returns (comparison, missing) where `missing` lists FEC states with no 2024
    general results file in `raw_dir`.
    """
    fec = load_fec(fec_path)
    states = [s.upper() for s in (states or fec.index)]
    rows, missing = {}, []
    for st in states:
        if st in NYT_STATES:
            rows[st] = nyt_vote_totals(raw_dir, st)
            continue
        path = find_precinct_results(raw_dir, st)
        if path is None:
            missing.append(st)
        else:
            rows[st] = state_vote_totals(path)
    comparison = compare_to_fec(pd.DataFrame(rows).T, fec, max_pct_diff, columns) if rows else pd.DataFrame()
    return comparison, missing
