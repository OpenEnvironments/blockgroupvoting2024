"""Allocate precinct vote counts onto block groups by overlapping land area."""

import geopandas as gpd
import pandas as pd

EQUAL_AREA_CRS = "EPSG:5070"


def allocate_votes(
    precincts,
    block_groups,
    vote_cols,
    precinct_id="precinct_id",
    bg_id="GEOID",
    land=None,
    land_fraction_col=None,
    crs=EQUAL_AREA_CRS,
    tol=1e-9,
):
    """Split each precinct's vote counts across the block groups it overlaps.

    Each precinct's counts are divided in proportion to the area of its overlap
    with each block group. If `land` (polygons of land only) is given, overlaps
    are clipped to it first so water does not absorb votes. If
    `land_fraction_col` names a block group column (land share of the block
    group, 0-1), each overlap area is scaled by it, which treats water as spread
    evenly through the block group. The denominator is the precinct's weighted
    area, so weights sum to 1 per precinct. `tol` is relative to the totals.

    Returns (allocated, unallocated_ids). `allocated` has one row per block
    group with the summed vote columns. `unallocated_ids` lists precincts with
    no overlap (their votes are not in `allocated`). Raises if the allocated
    totals do not equal the input totals of the allocated precincts.
    """
    vote_cols = list(vote_cols)
    if precincts[precinct_id].duplicated().any():
        raise ValueError(f"{precinct_id} is not unique in precincts")

    p = precincts[[precinct_id, *vote_cols, "geometry"]].to_crs(crs)
    b = block_groups[[bg_id, *([land_fraction_col] if land_fraction_col else []), "geometry"]].to_crs(crs)
    p["geometry"] = p.geometry.make_valid()
    b["geometry"] = b.geometry.make_valid()

    pieces = gpd.overlay(p[[precinct_id, "geometry"]], b, how="intersection", keep_geom_type=True)
    if land is not None:
        land_u = gpd.GeoDataFrame(geometry=land.to_crs(crs).geometry.make_valid()).dissolve()
        pieces = gpd.overlay(pieces, land_u, how="intersection", keep_geom_type=True)

    pieces["area"] = pieces.geometry.area
    if land_fraction_col:
        pieces["area"] = pieces["area"] * pieces[land_fraction_col]
    pieces = pieces[pieces["area"] > 0]
    pieces["weight"] = pieces["area"] / pieces.groupby(precinct_id)["area"].transform("sum")

    merged = pieces[[precinct_id, bg_id, "weight"]].merge(
        p[[precinct_id, *vote_cols]], on=precinct_id, how="left"
    )
    for col in vote_cols:
        merged[col] = merged[col] * merged["weight"]
    allocated = merged.groupby(bg_id)[vote_cols].sum()

    unallocated_ids = sorted(set(p[precinct_id]) - set(pieces[precinct_id]))
    expected = p.loc[~p[precinct_id].isin(unallocated_ids), vote_cols].sum()
    diff = (allocated.sum() - expected).abs()
    limit = tol * expected.clip(lower=1)
    if (diff > limit).any():
        raise AssertionError(f"Vote totals not conserved: {diff[diff > limit].to_dict()}")

    return allocated, unallocated_ids
