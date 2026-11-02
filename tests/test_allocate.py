import geopandas as gpd
import pytest
from shapely.geometry import box

from allocate import allocate_votes

CRS = "EPSG:5070"


def _gdf(rows, id_col):
    return gpd.GeoDataFrame(
        [{k: v for k, v in r.items() if k != "geom"} for r in rows],
        geometry=[r["geom"] for r in rows],
        crs=CRS,
    )


def _block_groups():
    return _gdf(
        [
            {"GEOID": "010010001001", "geom": box(0, 0, 1, 1)},
            {"GEOID": "010010001002", "geom": box(1, 0, 2, 1)},
        ],
        "GEOID",
    )


def test_even_split_and_conservation():
    precincts = _gdf([{"precinct_id": "A", "dem": 100, "rep": 40, "geom": box(0, 0, 2, 1)}], "precinct_id")
    out, unallocated = allocate_votes(precincts, _block_groups(), ["dem", "rep"])
    assert unallocated == []
    assert out.loc["010010001001", "dem"] == pytest.approx(50)
    assert out.loc["010010001002", "rep"] == pytest.approx(20)
    assert out["dem"].sum() == pytest.approx(100)


def test_uneven_split_by_area():
    precincts = _gdf([{"precinct_id": "A", "dem": 100, "geom": box(0, 0, 1.5, 1)}], "precinct_id")
    out, _ = allocate_votes(precincts, _block_groups(), ["dem"])
    assert out.loc["010010001001", "dem"] == pytest.approx(100 * 1 / 1.5)
    assert out.loc["010010001002", "dem"] == pytest.approx(100 * 0.5 / 1.5)


def test_precinct_extending_outside_block_groups_keeps_all_votes():
    precincts = _gdf([{"precinct_id": "A", "dem": 90, "geom": box(1, 0, 4, 1)}], "precinct_id")
    out, unallocated = allocate_votes(precincts, _block_groups(), ["dem"])
    assert unallocated == []
    assert out["dem"].sum() == pytest.approx(90)


def test_non_overlapping_precinct_is_reported_not_dropped_silently():
    precincts = _gdf(
        [
            {"precinct_id": "A", "dem": 10, "geom": box(0, 0, 1, 1)},
            {"precinct_id": "B", "dem": 99, "geom": box(10, 10, 11, 11)},
        ],
        "precinct_id",
    )
    out, unallocated = allocate_votes(precincts, _block_groups(), ["dem"])
    assert unallocated == ["B"]
    assert out["dem"].sum() == pytest.approx(10)


def test_land_mask_excludes_water():
    precincts = _gdf([{"precinct_id": "A", "dem": 100, "geom": box(0, 0, 2, 1)}], "precinct_id")
    land = gpd.GeoDataFrame(geometry=[box(0, 0, 1.5, 1)], crs=CRS)
    out, _ = allocate_votes(precincts, _block_groups(), ["dem"], land=land)
    assert out.loc["010010001001", "dem"] == pytest.approx(100 * 1 / 1.5)
    assert out["dem"].sum() == pytest.approx(100)


def test_land_fraction_column_shifts_votes_toward_land():
    bgs = _block_groups()
    bgs["land_fraction"] = [1.0, 0.5]
    precincts = _gdf([{"precinct_id": "A", "dem": 90, "geom": box(0, 0, 2, 1)}], "precinct_id")
    out, _ = allocate_votes(precincts, bgs, ["dem"], land_fraction_col="land_fraction")
    assert out.loc["010010001001", "dem"] == pytest.approx(60)
    assert out.loc["010010001002", "dem"] == pytest.approx(30)
    assert out["dem"].sum() == pytest.approx(90)


def test_precinct_entirely_in_water_is_reported_unallocated():
    bgs = _block_groups()
    bgs["land_fraction"] = [0.0, 1.0]
    precincts = _gdf([{"precinct_id": "A", "dem": 7, "geom": box(0, 0, 1, 1)}], "precinct_id")
    out, unallocated = allocate_votes(precincts, bgs, ["dem"], land_fraction_col="land_fraction")
    assert unallocated == ["A"]
    assert out.empty


def test_duplicate_precinct_ids_rejected():
    precincts = _gdf(
        [
            {"precinct_id": "A", "dem": 1, "geom": box(0, 0, 1, 1)},
            {"precinct_id": "A", "dem": 1, "geom": box(1, 0, 2, 1)},
        ],
        "precinct_id",
    )
    with pytest.raises(ValueError):
        allocate_votes(precincts, _block_groups(), ["dem"])
