import gzip
import json

import geopandas as gpd
import pytest
from shapely.geometry import box

from ingest import check_state_totals
from load import load_precincts
from nyt import NYT_CRS, load_nyt_precincts, nyt_vote_totals


def _topology(rows):
    """A tiny TopoJSON: one unit-square-ish polygon per row, shifted east by its index."""
    arcs, geoms = [], []
    for i, props in enumerate(rows):
        arcs.append([[i * 20, 0], [10, 0], [0, 10], [-10, 0], [0, -10]])
        geoms.append({"type": "Polygon", "arcs": [[i]], "properties": props})
    return {
        "type": "Topology",
        "arcs": arcs,
        "transform": {"scale": [0.001, 0.001], "translate": [-77.0, 38.9]},
        "objects": {"precincts": {"type": "GeometryCollection", "geometries": geoms}},
    }


def _props(state, geoid, dem, rep, total):
    return {
        "state": state, "GEOID": geoid, "votes_dem": dem, "votes_rep": rep,
        "votes_total": total, "pct_dem_lead": 0.0, "official_boundary": True,
    }


def _write_nyt(raw_dir, rows):
    folder = raw_dir / "nyt"
    folder.mkdir(parents=True)
    with gzip.open(folder / "precincts-with-results.topojson.gz", "wt") as f:
        json.dump(_topology(rows), f)


ROWS = [
    _props("DC", "11001-1", 10, 2, 13),
    _props("DC", "11001-2", 5, 1, 8),
    _props("VA", "51001-1", 99, 99, 200),
]


def test_load_nyt_precincts_filters_state_derives_other_and_caches(tmp_path):
    raw = tmp_path / "raw"
    _write_nyt(raw, ROWS)
    out = load_nyt_precincts(raw, "DC")
    assert list(out["precinct_id"]) == ["11001-1", "11001-2"]
    assert list(out["dem"]) == [10, 5] and list(out["rep"]) == [2, 1] and list(out["other"]) == [1, 2]
    assert out.crs.to_string() == NYT_CRS
    assert (tmp_path / "interim" / "nyt_dc_precincts.gpkg").exists()


def test_second_load_uses_cache_without_the_topojson(tmp_path):
    raw = tmp_path / "raw"
    _write_nyt(raw, ROWS)
    load_nyt_precincts(raw, "DC")
    (raw / "nyt" / "precincts-with-results.topojson.gz").unlink()
    assert len(load_nyt_precincts(raw, "DC")) == 2


def test_nyt_vote_totals(tmp_path):
    raw = tmp_path / "raw"
    _write_nyt(raw, ROWS)
    assert nyt_vote_totals(raw, "DC") == {"dem": 15.0, "rep": 3.0, "other": 3.0, "total": 21.0}


def test_negative_other_is_rejected(tmp_path):
    raw = tmp_path / "raw"
    _write_nyt(raw, [_props("DC", "11001-1", 10, 5, 12)])
    with pytest.raises(ValueError):
        load_nyt_precincts(raw, "DC")


def test_load_precincts_routes_dc_to_nyt(tmp_path):
    raw = tmp_path / "raw"
    _write_nyt(raw, ROWS)
    (raw / "precincts").mkdir()
    assert list(load_precincts(raw, "DC")["precinct_id"]) == ["11001-1", "11001-2"]


def test_check_state_totals_uses_nyt_for_dc_and_does_not_report_it_missing(tmp_path):
    raw = tmp_path / "raw"
    _write_nyt(raw, ROWS)
    (raw / "precincts").mkdir()
    (raw / "fec").mkdir()
    fec = raw / "fec" / "fec.csv"
    fec.write_bytes(b'State,Democratic (Harris),Republican (Trump),All other\r\nDC,"15","3","3"\r\n'
                    b'U.S. total,"15","3","3"\r\n')
    comparison, missing = check_state_totals(raw, fec, states=["DC"])
    assert missing == []
    assert bool(comparison.loc["DC", "ok"]) is True
