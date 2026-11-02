# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

2024 General Election voting by US Census Block Group (per `README.md`). The goal is to allocate 2024 voting precinct results onto Census block group geographies using geopandas, weighting by overlapping land area (areal interpolation). This is a GIS allocation task, not a machine learning one. Licensed under the terms in `LICENSE`.

## Current state

Working pipeline, run per state: `src/load.py` (precinct and block group loaders) feeds `src/allocate.py` `allocate_votes()` (areal-weighted allocation, conservation check, list of unallocated precincts), driven by `src/run_state.py`. `src/ingest.py` and `src/check_totals.py` compare precinct totals to the FEC. There is no lint config or dependency manifest yet. Fill in the TODOs below as decisions are made.

Water handling: no water layer is available, so each overlap area is scaled by its block group's land fraction, `ALAND / (ALAND + AWATER)`, which assumes water is spread evenly through the block group. A precinct whose overlaps all have zero land weight is reported as unallocated rather than dropped silently. Allocation uses EPSG:5070 (Alaska EPSG:3338, Hawaii ESRI:102007).

FEC acceptance criterion: judge Harris and Trump only (`--columns dem rep`, the default for `run_state.py --fec-ok`), at a 0.1% tolerance. The user reviewed and accepted the remaining differences: 35 states match exactly and the other 15 differ by at most 0.083% (UT, CA, NC largest). The "All other" column is not used as a gate, since it differs in 18 states (e.g. AZ −842, NY +41,530, PA −24,526) and the cause has not been investigated. DC is covered by the NYT dataset rather than RDH (see DC precincts above).

## Environment and commands

Use the conda env `blockgroupvoting2024` (geopandas 1.2, shapely 2.1, pandas 3.0, pyogrio). `pytest` was not installed in it when this was written (`conda install -n blockgroupvoting2024 pytest`).

The shell may have `PROJ_LIB` and `PROJ_DATA` set to a different env (`geotools`), which makes pyproj warn and CRS operations fail. Point them at this env's own PROJ data before running anything:

```
set PROJ_LIB=C:\Users\micha\anaconda3\envs\blockgroupvoting2024\Library\share\proj
set PROJ_DATA=%PROJ_LIB%
```

Check precinct-level results against the FEC state totals with `python src/check_totals.py [--states AZ TX] [--max-pct-diff 0.001]` (run from the repo root). It reads the zips in `data/raw/precincts/` directly and the FEC CSV in `data/raw/fec/`, sums Harris, Trump and all other presidential votes per state (`src/ingest.py`), and prints per-state differences, exiting 1 if any state is outside the tolerance. States with no 2024 general file are listed, not checked. Harris and Trump are matched by exact column name (`G24PREDHAR`, `G24PRERTRU`, or `PREDEM24`/`PREREP24` for WI), because other-party columns can also start with `G24PRED`. The FEC file has a trailing "U.S. total" row, which `load_fec` uses as an internal consistency check.

Allocate precinct votes onto block groups with `python src/run_state.py --states RI VT`, or `--fec-ok` for every state that passes the FEC check. Output is `data/processed/{st}_blockgroup_votes.csv` with columns `REP`, `DEM`, `OTH`, `STATE` (postal abbreviation) and `BLOCKGROUP_GEOID` (12-character string, so read it with `dtype=str`), and the script prints votes in versus out, plus any unallocated precincts, per state. It exits 1 if any state fails (for example, votes not conserved).

Run tests with `pytest tests`, or a single test with `pytest tests/test_allocate.py::test_even_split_and_conservation`. `tests/conftest.py` puts `src/` on the import path.

## Project definition (TODO: fill in)

- **Precinct data:** Redistricting Data Hub (RDH), downloaded as zips into `data/raw/precincts/` (read directly with `zip://`, nothing is unzipped). The folder holds true 2024 general precinct polygons, one zip per state: `{st}_2024_gen_prec.zip` (Texas is `tx_2024_gen_tx_vtd.zip`), 50 states and no DC (DC comes from the NYT dataset, below). Many zips hold several layers (`all`, `cong`, `sldl`, `sldu`); use the `_all_` layer for statewide results. California ships as GeoJSON instead of a shapefile. The CRS differs by state (EPSG:3857, 4326, UTM zones, geographic NAD83, 6514, ...), so reproject before computing areas. Vote columns: `G24PREDHAR` (Harris) and `G24PRERTRU` (Trump), and every other `G24PRE*` column is another presidential candidate. Wisconsin is the exception: it has no `G24PRE*` columns, only `PREDEM24`, `PREREP24`, other `PRE???24`/`PRENP?24` candidates, and a `PRETOT24` statewide total that must not be counted as a candidate.
- **DC precincts (NYT):** RDH has no DC file, so DC comes from `data/raw/nyt/precincts-with-results.topojson.gz`, the New York Times national 2024 precinct dataset, published at https://github.com/nytimes/presidential-precinct-map-2024 (127,270 precincts in 45 states; fields `state`, `GEOID`, `votes_dem`, `votes_rep`, `votes_total`, `pct_dem_lead`, `official_boundary`). `src/nyt.py` routes the states in `NYT_STATES` (currently just `DC`) through it, and every other state still comes from RDH. The TopoJSON declares no CRS; its coordinates are lon/lat, so EPSG:4326 is assumed (checked on load). `other` is derived as `votes_total - votes_dem - votes_rep`. Reading the national file takes about 2.5 minutes, so the first use caches that state's rows in `data/interim/nyt_{st}_precincts.gpkg` (delete it to re-extract). DC has 144 precincts, 17 with invalid geometry (repaired by the allocator), and its totals equal the FEC exactly on all three columns (Harris 294,185, Trump 21,076, other 10,608).
- **NYT citation and license** (summarised from the repo's README and LICENSE; confirm against the originals before relying on it): "Presidential precinct data for the 2024 U.S. general election", The New York Times, contact electionsdata@nytimes.com. The README asks users to cite it and link to the map, https://www.nytimes.com/interactive/2025/us/elections/2024-election-map-precinct-results.html, with this suggested citation: "2024 Precinct-Level Election Results." *New York Times*, www.nytimes.com/interactive/2025/us/elections/2024-election-map-precinct-results.html. Accessed [date accessed]. The license is the NYT Computational Use of Data Agreement v1.0 - Non-Commercial: computational use, credit to The New York Times required, non-commercial use only (with an exception for editorial use by journalists), and redistribution only with attribution kept and recipients bound by the same terms. The README gives no publication date or version and says the data is updated occasionally (the repo's commit history runs to January 2026), while the local file's timestamp is March 22, 2025, so record the download date; DC still matches the FEC exactly. `votes_total` includes third-party and write-in votes when the source reports them, `official_boundary` is true when the shape came from a state or county file (true for all 144 DC precincts), and the README marks DC as fully covered. The README does not state a CRS and does not document the `id` field.
- **Block groups:** TIGER/Line 2024 (`tl_2024_{statefp}_bg.zip` in `data/raw/blockgroups/`, one per state plus territories, EPSG:4269, 12-character `GEOID`, with `ALAND`/`AWATER`). Block `GEOID20[:12]` is the block group GEOID, since blocks nest in block groups.
- **FEC state totals (validation only):** `data/raw/fec/Federal Election Commission, Official 2024 Presidential General Election Results.csv`. Citation: Federal Election Commission, Official 2024 Presidential General Election Results, compiled from state election offices, January 16, 2025. Harris figures are from page 3, Trump from page 5, and total votes from page 6. PDF: https://www.fec.gov/documents/5644/2024presgeresults.pdf. The CSV's `All other` column is not one of the cited PDF figures; it is consistent with total minus Harris minus Trump (checked for DC: 325,869 - 294,185 - 21,076 = 10,608), but how it was produced is not documented here.
- **Vote fields to allocate:** 2024 presidential votes as `dem` (Harris), `rep` (Trump) and `other` (all other candidates) internally; the output files call them `DEM`, `REP` and `OTH`.
- **Geographic scope:** all 50 states plus DC, run per state. The 18 states that failed the full FEC check were run too, after the Harris/Trump-only criterion was accepted.
- **Environment and dependencies:** TODO

## Allocation method

For each precinct, split each vote count across the block groups it overlaps in proportion to the share of the precinct's land area that falls in each block group. Sum the pieces per block group.

Rules that matter for correctness:

- **Use an equal-area projection for area calculations.** Compute overlaps and areas in a projected equal-area CRS (e.g. EPSG:5070 for the contiguous US), never in geographic lat/lon. Reproject both layers to the same CRS before `overlay`.
- **Weight by land area, not total area.** Exclude water so that offshore or lake slivers don't absorb votes. Block groups carry `ALAND` and `AWATER`; precinct layers usually don't, so clip precincts to land (for example against the block group layer or a water layer) before computing weights, and document which approach is used.
- **Denominator is the precinct's land area after clipping,** not its original polygon area. Otherwise weights won't sum to 1 and votes leak out.
- **Conserve totals.** For each precinct, the allocated pieces must sum to the original vote count, and state or county totals before and after allocation must match. Check this after every run and fail loudly on drift.
- **Handle precincts that don't overlap any block group** (or have zero land area) explicitly: report them and decide on a fallback, rather than dropping their votes silently.
- **Repair invalid geometries** (`make_valid` or a zero buffer) before overlay, and drop or merge the tiny sliver polygons that overlay produces only after weights are computed, so their votes are redistributed rather than lost.
- **Areal weighting assumes votes are spread evenly across a precinct's land.** It is an estimate, and it's weakest for large rural precincts containing an uneven population. Keep that caveat in any output documentation.
- **Keep GEOIDs as zero-padded strings** (state + county + tract + block group). Reading them as integers drops leading zeros and breaks joins.
- **Record the vintage and source of every input layer,** since precinct and block group boundaries both change over time.
- **Don't commit raw data.** Keep `data/` gitignored and document how to re-download each source.

## Layout

`src/load.py` loads one state's layers (RDH, or NYT for DC via `src/nyt.py`), `src/allocate.py` holds the allocation logic, `src/ingest.py` + `src/check_totals.py` validate against the FEC, and `src/run_state.py` runs a state end to end. Inputs live in `data/raw/{precincts,blockgroups,fec}` and outputs in `data/processed`, both gitignored. Extend this section as stages are added.
