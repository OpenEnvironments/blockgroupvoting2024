import json
import zipfile

import pandas as pd
import pytest

from ingest import (
    classify_presidential_columns,
    compare_to_fec,
    find_precinct_results,
    load_fec,
    state_vote_totals,
)


def _write_fec(path, rows, us_total):
    lines = ["State,Democratic (Harris),Republican (Trump),All other"]
    lines += [f'{s},"{d:,}","{r:,}","{o:,}"' for s, d, r, o in rows]
    lines.append('U.S. total,"{:,}","{:,}","{:,}"'.format(*us_total))
    path.write_bytes(("﻿" + "\r\n".join(lines) + "\r\n").encode("utf-8"))


def _write_zip(path, name, text):
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("README.txt", "readme")
        zf.writestr(name, text)


def test_load_fec_parses_bom_and_thousands_separators(tmp_path):
    p = tmp_path / "fec.csv"
    _write_fec(p, [("AL", 1000, 2000, 30), ("AK", 1500, 2500, 70)], (2500, 4500, 100))
    fec = load_fec(p)
    assert list(fec.index) == ["AL", "AK"]
    assert fec.loc["AL", "total"] == 3030
    assert fec.loc["AK", "rep"] == 2500


def test_load_fec_rejects_state_rows_not_matching_us_total(tmp_path):
    p = tmp_path / "fec.csv"
    _write_fec(p, [("AL", 1000, 2000, 30)], (999, 2000, 30))
    with pytest.raises(ValueError):
        load_fec(p)


def test_classify_uses_exact_harris_and_trump_columns():
    cols = ["GEOID20", "G24PRO133N", "G24PREDHAR", "G24PREDPER", "G24PRERTRU", "G24PRELOLI", "G24USSDGAL"]
    groups = classify_presidential_columns(cols)
    assert groups == {"dem": ["G24PREDHAR"], "rep": ["G24PRERTRU"], "other": ["G24PREDPER", "G24PRELOLI"]}


def test_classify_wisconsin_columns_exclude_precinctid():
    cols = ["PRECINCTID", "PREDEM24", "PREREP24", "PRECON24", "PRENP124", "PRETOT24", "USSDEM24"]
    groups = classify_presidential_columns(cols)
    assert groups["dem"] == ["PREDEM24"] and groups["rep"] == ["PREREP24"]
    assert groups["other"] == ["PRECON24", "PRENP124"]


def test_classify_rejects_unknown_layout():
    with pytest.raises(ValueError):
        classify_presidential_columns(["GEOID20", "VAP_MOD"])


def _write_geojson_zip(path, layer, votes):
    features = [
        {"type": "Feature", "geometry": None, "properties": v} for v in votes
    ]
    _write_zip(path, layer, json.dumps({"type": "FeatureCollection", "features": features}))


def test_state_vote_totals_sums_geojson_zip(tmp_path):
    z = tmp_path / "xx_2024_gen_prec.zip"
    _write_geojson_zip(
        z,
        "xx_2024_gen_prec.geojson",
        [
            {"G24PREDHAR": 10, "G24PRERTRU": 20, "G24PRELOLI": 1, "G24USSDGAL": 99},
            {"G24PREDHAR": 5, "G24PRERTRU": 4, "G24PRELOLI": 2, "G24USSDGAL": 99},
        ],
    )
    totals = state_vote_totals(z)
    assert totals == {"dem": 15.0, "rep": 24.0, "other": 3.0, "total": 42.0}


def test_state_vote_totals_uses_all_layer_when_zip_has_several(tmp_path):
    z = tmp_path / "xx_2024_gen_prec.zip"
    with zipfile.ZipFile(z, "w") as zf:
        for layer, dem in (("xx_2024_gen_all_prec", 10), ("xx_2024_gen_cong_prec", 999)):
            row = {"type": "Feature", "geometry": None, "properties": {"G24PREDHAR": dem, "G24PRERTRU": 1}}
            zf.writestr(f"{layer}/{layer}.geojson", json.dumps({"type": "FeatureCollection", "features": [row]}))
    assert state_vote_totals(z)["dem"] == 10.0


def test_find_precinct_results_matches_prec_and_vtd_names_and_reports_missing(tmp_path):
    folder = tmp_path / "rdh"
    folder.mkdir()
    (folder / "az_2024_gen_prec.zip").write_bytes(b"")
    (folder / "az_2024_gen_2020_blocks_csv.zip").write_bytes(b"")
    (folder / "tx_2024_gen_tx_vtd.zip").write_bytes(b"")
    assert find_precinct_results(tmp_path, "AZ").name == "az_2024_gen_prec.zip"
    assert find_precinct_results(tmp_path, "tx").name == "tx_2024_gen_tx_vtd.zip"
    assert find_precinct_results(tmp_path, "DC") is None


def test_compare_flags_only_states_outside_tolerance():
    fec = pd.DataFrame(
        {"dem": [1000, 1000], "rep": [2000, 2000], "other": [100, 100], "total": [3100, 3100]},
        index=["AL", "AK"],
    )
    results = pd.DataFrame(
        {"dem": [1000.0, 1000.0], "rep": [2000.0, 2000.0], "other": [100.0, 50.0], "total": [3100.0, 3050.0]},
        index=["AL", "AK"],
    )
    out = compare_to_fec(results, fec, max_pct_diff=0.001)
    assert bool(out.loc["AL", "ok"]) is True
    assert bool(out.loc["AK", "ok"]) is False
    assert out.loc["AK", "other_diff"] == -50
    only_two = compare_to_fec(results, fec, max_pct_diff=0.001, columns=["dem", "rep"])
    assert only_two["ok"].all()
    assert only_two.loc["AK", "other_diff"] == -50
