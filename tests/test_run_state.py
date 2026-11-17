import pandas as pd

from run_state import OUTPUT_COLUMNS, format_output


def test_format_output_renames_columns_and_adds_state():
    allocated = pd.DataFrame(
        {"dem": [10.0, 5.0], "rep": [20.0, 4.0], "other": [1.0, 0.5], "precinct_count": [3, 1]},
        index=pd.Index(["440010001001", "440010001002"], name="GEOID"),
    )
    out = format_output(allocated, "ri")
    assert list(out.columns) == OUTPUT_COLUMNS == ["REP", "DEM", "OTH", "STATE", "BLOCKGROUP_GEOID", "PRECINCTS", "TOT"]
    assert list(out["TOT"]) == [31.0, 9.5]
    assert list(out["PRECINCTS"]) == [3, 1]
    assert list(out["BLOCKGROUP_GEOID"]) == ["440010001001", "440010001002"]
    assert list(out["STATE"]) == ["RI", "RI"]
    assert list(out["REP"]) == [20.0, 4.0]
    assert list(out["DEM"]) == [10.0, 5.0]
    assert list(out["OTH"]) == [1.0, 0.5]
