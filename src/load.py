"""Load one state's precinct results and block groups as GeoDataFrames."""

from pathlib import Path

import geopandas as gpd
import pyogrio

from ingest import VOTE_KEYS, classify_presidential_columns, find_precinct_results, pick_layer
from nyt import NYT_STATES, load_nyt_precincts

STATE_FIPS = {
    "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06", "CO": "08", "CT": "09", "DE": "10",
    "DC": "11", "FL": "12", "GA": "13", "HI": "15", "ID": "16", "IL": "17", "IN": "18", "IA": "19",
    "KS": "20", "KY": "21", "LA": "22", "ME": "23", "MD": "24", "MA": "25", "MI": "26", "MN": "27",
    "MS": "28", "MO": "29", "MT": "30", "NE": "31", "NV": "32", "NH": "33", "NJ": "34", "NM": "35",
    "NY": "36", "NC": "37", "ND": "38", "OH": "39", "OK": "40", "OR": "41", "PA": "42", "RI": "44",
    "SC": "45", "SD": "46", "TN": "47", "TX": "48", "UT": "49", "VT": "50", "VA": "51", "WA": "53",
    "WV": "54", "WI": "55", "WY": "56",
}

# Equal-area CRS for area weighting; the contiguous-US default is EPSG:5070 (see allocate.py)
EQUAL_AREA_CRS = {"AK": "EPSG:3338", "HI": "ESRI:102007"}


def load_precincts(raw_dir, state):
    """Precinct polygons with presidential votes summed into dem, rep, other.

    Comes from RDH, except for the states in `nyt.NYT_STATES` (DC), which come
    from the NYT dataset. Returns a GeoDataFrame with a unique `precinct_id` ("{ST}-{row}"), the
    `dem`, `rep` and `other` vote columns, and geometry in its original CRS.
    """
    if state.upper() in NYT_STATES:
        return load_nyt_precincts(raw_dir, state)
    path = find_precinct_results(raw_dir, state)
    if path is None:
        raise FileNotFoundError(f"no 2024 general precinct file for {state}")
    uri = f"zip://{path}!{pick_layer(path)}"
    groups = classify_presidential_columns(pyogrio.read_info(uri)["fields"])
    gdf = gpd.read_file(uri, columns=sum(groups.values(), []))
    if gdf.crs is None:
        raise ValueError(f"{state} precinct layer has no CRS")
    out = gpd.GeoDataFrame(
        {"precinct_id": [f"{state.upper()}-{i}" for i in range(len(gdf))]},
        geometry=gdf.geometry,
        crs=gdf.crs,
    )
    for key in VOTE_KEYS:
        out[key] = gdf[groups[key]].sum(axis=1).astype(float)
    return out


def find_block_groups(raw_dir, state):
    """Path to the state's TIGER/Line block group zip (`tl_{vintage}_{fips}_bg.zip`, any vintage)."""
    fips = STATE_FIPS[state.upper()]
    found = sorted((Path(raw_dir) / "blockgroups").glob(f"tl_*_{fips}_bg.zip"))
    if not found:
        raise FileNotFoundError(f"no block group file for {state} (tl_*_{fips}_bg.zip)")
    if len(found) > 1:
        raise ValueError(f"several block group vintages for {state}: {[p.name for p in found]}")
    return found[0]


def load_block_groups(raw_dir, state):
    """TIGER block groups with `GEOID` (string), `ALAND`, `AWATER` and `land_fraction`."""
    path = find_block_groups(raw_dir, state)
    gdf = gpd.read_file(f"zip://{path}", columns=["GEOID", "ALAND", "AWATER"])
    gdf["GEOID"] = gdf["GEOID"].astype(str)
    total = gdf["ALAND"] + gdf["AWATER"]
    gdf["land_fraction"] = (gdf["ALAND"] / total).where(total > 0, 0.0)
    return gdf
