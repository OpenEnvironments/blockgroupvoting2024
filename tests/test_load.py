import json
import zipfile

import geopandas as gpd
import pytest
from shapely.geometry import box, mapping

from load import STATE_FIPS, load_block_groups, load_precincts


def _write_precinct_zip(raw_dir, state, rows):
    folder = raw_dir / "precincts"
    folder.mkdir(parents=True)
    features = [
        {"type": "Feature", "geometry": mapping(geom), "properties": props} for geom, props in rows
    ]
    fc = {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::4326"}},
        "features": features,
    }
    with zipfile.ZipFile(folder / f"{state}_2024_gen_prec.zip", "w") as zf:
        zf.writestr(f"{state}_2024_gen_prec.geojson", json.dumps(fc))


def test_load_precincts_sums_vote_groups_and_assigns_unique_ids(tmp_path):
    _write_precinct_zip(
        tmp_path,
        "xx",
        [
            (box(0, 0, 1, 1), {"G24PREDHAR": 10, "G24PRERTRU": 20, "G24PRELOLI": 1, "G24PREGSTE": 2}),
            (box(1, 0, 2, 1), {"G24PREDHAR": 5, "G24PRERTRU": 4, "G24PRELOLI": 0, "G24PREGSTE": 1}),
        ],
    )
    out = load_precincts(tmp_path, "XX")
    assert list(out["precinct_id"]) == ["XX-0", "XX-1"]
    assert list(out["dem"]) == [10, 5]
    assert list(out["rep"]) == [20, 4]
    assert list(out["other"]) == [3, 1]
    assert out.crs is not None


def test_load_precincts_missing_file_raises(tmp_path):
    (tmp_path / "precincts").mkdir()
    with pytest.raises(FileNotFoundError):
        load_precincts(tmp_path, "XX")


def test_load_block_groups_keeps_geoid_string_and_computes_land_fraction(tmp_path):
    folder = tmp_path / "blockgroups"
    folder.mkdir()
    bgs = gpd.GeoDataFrame(
        {
            "GEOID": ["440010001001", "440010001002"],
            "ALAND": [750, 0],
            "AWATER": [250, 0],
        },
        geometry=[box(0, 0, 1, 1), box(1, 0, 2, 1)],
        crs="EPSG:4269",
    )
    shp_dir = tmp_path / "shp"
    shp_dir.mkdir()
    bgs.to_file(shp_dir / "tl_2024_44_bg.shp")
    with zipfile.ZipFile(folder / "tl_2024_44_bg.zip", "w") as zf:
        for f in shp_dir.iterdir():
            zf.write(f, f.name)
    out = load_block_groups(tmp_path, "RI")
    assert list(out["GEOID"]) == ["440010001001", "440010001002"]
    assert list(out["land_fraction"]) == [0.75, 0.0]


def test_state_fips_covers_50_states_and_dc():
    assert len(STATE_FIPS) == 51
    assert STATE_FIPS["RI"] == "44" and STATE_FIPS["AL"] == "01"
