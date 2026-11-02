"""Load precinct results from the NYT 2024 precinct dataset, for states RDH does not cover."""

from pathlib import Path

import geopandas as gpd
import pyogrio

NYT_STATES = {"DC"}
NYT_FILE = "precincts-with-results.topojson.gz"
# The TopoJSON declares no CRS; the coordinates are lon/lat (checked on extraction)
NYT_CRS = "EPSG:4326"


def _cache_path(raw_dir, state):
    return Path(raw_dir).parent / "interim" / f"nyt_{state.lower()}_precincts.gpkg"


def extract_nyt_state(raw_dir, state):
    """Read the national NYT file (slow, a couple of minutes) and cache one state's precincts."""
    path = Path(raw_dir).resolve() / "nyt" / NYT_FILE
    if not path.exists():
        raise FileNotFoundError(f"NYT precinct file not found: {path}")
    gdf = pyogrio.read_dataframe(f"/vsigzip/{path}")
    gdf = gdf[gdf["state"] == state.upper()].copy()
    if gdf.empty:
        raise ValueError(f"no {state} precincts in {path.name}")
    minx, miny, maxx, maxy = gdf.total_bounds
    if not (-180 <= minx and maxx <= 180 and -90 <= miny and maxy <= 90):
        raise ValueError(f"{state} NYT coordinates are not lon/lat: {gdf.total_bounds}")
    gdf = gdf.set_crs(NYT_CRS)
    cache = _cache_path(raw_dir, state)
    cache.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(cache, driver="GPKG")
    return gdf


def _read_state(raw_dir, state, geometry):
    cache = _cache_path(raw_dir, state)
    if not cache.exists():
        extract_nyt_state(raw_dir, state)
    return pyogrio.read_dataframe(cache, read_geometry=geometry)


def _votes(df):
    """dem, rep and other (total minus the two) per precinct."""
    out = df[["votes_dem", "votes_rep"]].rename(columns={"votes_dem": "dem", "votes_rep": "rep"}).astype(float)
    out["other"] = df["votes_total"].astype(float) - out["dem"] - out["rep"]
    if (out < 0).any().any():
        raise ValueError("NYT votes_total is smaller than dem + rep in some precincts")
    return out


def load_nyt_precincts(raw_dir, state):
    """Precinct polygons with `precinct_id` (the NYT GEOID), `dem`, `rep` and `other` votes."""
    gdf = _read_state(raw_dir, state, geometry=True)
    if gdf["GEOID"].duplicated().any():
        raise ValueError(f"{state} NYT GEOIDs are not unique")
    out = gpd.GeoDataFrame({"precinct_id": gdf["GEOID"].astype(str)}, geometry=gdf.geometry, crs=gdf.crs)
    return out.join(_votes(gdf))


def nyt_vote_totals(raw_dir, state):
    """Sum a state's NYT presidential votes into dem, rep, other and total."""
    votes = _votes(_read_state(raw_dir, state, geometry=False))
    totals = {key: float(votes[key].sum()) for key in ("dem", "rep", "other")}
    totals["total"] = sum(totals.values())
    return totals
