import pandas as pd
import pytest

import combine_outputs
from combine_outputs import combine
from load import STATE_FIPS
from run_state import OUTPUT_COLUMNS


def _write(folder, st, geoid):
    row = {"REP": 1.0, "DEM": 2.0, "OTH": 0.5, "STATE": st, "BLOCKGROUP_GEOID": geoid, "PRECINCTS": 1, "TOT": 3.5}
    pd.DataFrame([row])[OUTPUT_COLUMNS].to_csv(folder / f"{st.lower()}_blockgroup_votes.csv", index=False)


def test_combine_keeps_geoid_strings_and_orders_by_state(tmp_path):
    for i, st in enumerate(sorted(STATE_FIPS, reverse=True)):
        _write(tmp_path, st, f"{i:012d}")
    out = combine(tmp_path)
    assert list(out.columns) == OUTPUT_COLUMNS
    assert len(out) == 51
    assert list(out["STATE"]) == sorted(STATE_FIPS)
    assert out["BLOCKGROUP_GEOID"].str.len().eq(12).all()


def test_combine_raises_when_a_state_is_missing(tmp_path):
    for st in sorted(STATE_FIPS)[:-1]:
        _write(tmp_path, st, f"{st}0000000000")
    with pytest.raises(FileNotFoundError):
        combine(tmp_path)
