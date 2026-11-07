# Data sources

Last updated 2026-11-03. Four sources feed this project. Raw files live in `data/raw/` (gitignored) and are not redistributed here.

Exact download dates were not recorded, so each source is given as "accessed on or before" a date: 2026-10-28 (the date the pipeline was first run on this data) for RDH, NYT and FEC, and 2026-11-07 for the Census block groups, which were replaced after that. Download locations were not recorded either. Statements about licenses are summaries of what the source files or repositories say; confirm against the originals before relying on them.

| Source | Used for | Local folder |
|---|---|---|
| Redistricting Data Hub (RDH) | Precinct boundaries and 2024 results, 50 states | `data/raw/precincts/` |
| The New York Times | Precinct boundaries and 2024 results, DC only | `data/raw/nyt/` |
| U.S. Census Bureau TIGER/Line 2021 | Block group boundaries and land/water area | `data/raw/blockgroups/` |
| Federal Election Commission (FEC) | State totals used to validate the precinct data | `data/raw/fec/` |

## 1. Redistricting Data Hub: 2024 general election precincts

- **What:** one zip per state, `{st}_2024_gen_prec.zip` (Texas is `tx_2024_gen_tx_vtd.zip`), holding precinct polygons with 2024 general election results. 50 states, no DC.
- **Publisher:** Redistricting Data Hub (https://redistrictingdatahub.org). Each zip includes a `README.txt` with a "Sources" section and an "RDH Date Retrieval" date. RDH assembles these from state and local election offices and other contributors, so the upstream source differs by state (table below).
- **Date accessed / download location:** accessed on or before 2026-10-28; download location not recorded. An earlier Arizona README gave the dataset page as `redistrictingdatahub.org/dataset/arizona-2024-general-election-precinct-level-results-and-boundaries/`; the current zips do not repeat it.
- **Credit required by RDH's terms:** the terms require credit "for any and all uses", with these suggested lines: "This map was created using data from the Redistricting Data Hub." / "This analysis was conducted using data from the Redistricting Data Hub." / "This data was obtained from the Redistricting Data Hub." (for reposting data) / "This data was generated using data from the Redistricting Data Hub." (for generated data). Output files from this project are generated data, so the last line is the closest fit; confirm with RDH if unsure.
- **Citation:** the READMEs contain no formal citation text. Suggested form, built from the README fields (not RDH's own wording): Redistricting Data Hub. *{State} 2024 General Election Precinct Boundaries and Election Results.* Data retrieved by RDH on {retrieval date from table}. https://redistrictingdatahub.org. Accessed on or before 2026-10-28. Also credit the upstream source named for that state.
- **License / terms:** [Terms and Conditions of Use](https://redistrictingdatahub.org/terms-and-conditions/), page last updated June 24, 2021 (summarised from the page on 2026-11-03; confirm against the original). The site is run by New Venture Fund on behalf of its Redistricting Data Hub project. In summary:
  - Use of the website and any data from it is for noncommercial use only, not for resale, and in a nonpartisan manner that does not involve gerrymandering (the page defines the term). Any other use needs RDH's prior consent.
  - Data may be made available to others, in whole or in part, only if they agree to the same terms. The page refers to a "Data License Agreement" that it neither defines nor links.
  - Not allowed: automated access beyond what a person could produce with a normal browser, sharing login credentials, and sharing incumbent address data.
  - Content is provided "AS IS" with no warranty of accuracy or completeness. The page does not name an upstream-data license or a Creative Commons license, and does not separately address derivative works or publication.
- **Field naming:** the READMEs describe a VEST-derived scheme, `G24` + office + party letter + first three letters of the candidate's surname (for example `G24PREDHAR`, Harris). Wisconsin uses a different scheme (`PREDEM24`, `PREREP24`, `PRETOT24`).
- **Caveats worth knowing:** Wisconsin's results are on January 2025 ward boundaries, newer than the election, disaggregated by the state. New Jersey's README gives no retrieval date. Colorado's first source line mentions a 2022 statewide precinct file, so check its boundary vintage. Louisiana's first source line is only "Election Results (November 5th)", and Texas lists "Texas Capitol Data Portal" with no link; read those READMEs for details.

### Per-state sources

"Results source" is the first source each README names; boundary sources and further details are in the README inside each zip.

| State | File | RDH retrieval date (as written) | Results source named first |
|---|---|---|---|
| AK | `ak_2024_gen_prec.zip` | 06/24/25 | Alaska Division of Elections |
| AL | `al_2024_gen_prec.zip` | 04/21/25 | Alabama Secretary of State |
| AR | `ar_2024_gen_prec.zip` | 10/12/26 | Arkansas Secretary of State |
| AZ | `az_2024_gen_prec.zip` | 06/16/2025 | OpenElections (Mohave County transcribed by RDH), cleaned to match the Arizona Secretary of State canvass |
| CA | `ca_2024_gen_prec.zip` | 12/02/2025 | California Statewide Database |
| CO | `co_2024_gen_prec.zip` | 01/20/25 | Colorado Secretary of State |
| CT | `ct_2024_gen_prec.zip` | 7/3/26 | Connecticut Secretary of State historical elections archive |
| DE | `de_2024_gen_prec.zip` | 04/8/26 | Delaware Department of Elections |
| FL | `fl_2024_gen_prec.zip` | 05/11/26 | Florida Division of Elections |
| GA | `ga_2024_gen_prec.zip` | 07/31/25 | Georgia Secretary of State |
| HI | `hi_2024_gen_prec.zip` | 4/8/26 | Hawaii Office of Elections |
| IA | `ia_2024_gen_prec.zip` | 06/01/26 | Iowa Secretary of State |
| ID | `id_2024_gen_prec.zip` | 2/4/26 | Idaho Secretary of State |
| IL | `il_2024_gen_prec.zip` | 10/08/25 | Illinois State Board of Elections |
| IN | `in_2024_gen_prec.zip` | 09/27/26 | Indiana Secretary of State |
| KS | `ks_2024_gen_prec.zip` | 09/12/2025 | IKE Lab |
| KY | `ky_2024_gen_prec.zip` | 10/10/25 | Kentucky State Board of Elections |
| LA | `la_2024_gen_prec.zip` | 03/02/25 | see README |
| MA | `ma_2024_gen_prec.zip` | 01/09/26 | Massachusetts Elections Division (boundaries primarily MassGIS) |
| MD | `md_2024_gen_prec.zip` | 08/21/25 | Maryland State Board of Elections |
| ME | `me_2024_gen_prec.zip` | 08/03/26 | Maine Secretary of State (municipal-level) |
| MI | `mi_2024_gen_prec.zip` | 7/20/26 | Michigan Secretary of State |
| MN | `mn_2024_gen_prec.zip` | 01/16/26 | Minnesota Secretary of State |
| MO | `mo_2024_gen_prec.zip` | 09/09/25 | OpenElections |
| MS | `ms_2024_gen_prec.zip` | 08/28/26 | Mississippi Secretary of State |
| MT | `mt_2024_gen_prec.zip` | 4/8/26 | Montana Secretary of State |
| NC | `nc_2024_gen_prec.zip` | 09/12/2025 | North Carolina State Board of Elections |
| ND | `nd_2024_gen_prec.zip` | 4/20/26 | North Dakota Secretary of State |
| NE | `ne_2024_gen_prec.zip` | 11/14/25 | Nebraska Secretary of State |
| NH | `nh_2024_gen_prec.zip` | 08/05/25 | New Hampshire Secretary of State |
| NJ | `nj_2024_gen_prec.zip` | not stated | County election offices and OpenElections (see README for the check source) |
| NM | `nm_2024_gen_prec.zip` | 4/22/26 | New Mexico Secretary of State |
| NV | `nv_2024_gen_prec.zip` | 02/19/26 | Nevada Secretary of State |
| NY | `ny_2024_gen_prec.zip` | 02/09/26 | Ben Rosenblatt (boundaries and results) |
| OH | `oh_2024_gen_prec.zip` | 05/01/25 | Redistricting Data Hub election results file |
| OK | `ok_2024_gen_prec.zip` | 10/17/26 | Oklahoma State Election Board |
| OR | `or_2024_gen_prec.zip` | 09/18/26 | Oregon Secretary of State via OpenElections |
| PA | `pa_2024_gen_prec.zip` | 10/14/26 | Pennsylvania Department of State |
| RI | `ri_2024_gen_prec.zip` | 2/22/26 | Rhode Island State Board of Elections |
| SC | `sc_2024_gen_prec.zip` | 12/20/2024 | South Carolina Secretary of State |
| SD | `sd_2024_gen_prec.zip` | 08/06/26 | South Dakota Secretary of State |
| TN | `tn_2024_gen_prec.zip` | 03/13/26 | Tennessee Secretary of State |
| TX | `tx_2024_gen_tx_vtd.zip` | 07/11/25 | Texas Capitol Data Portal (no link given) |
| UT | `ut_2024_gen_prec.zip` | 09/24/2025 | State of Utah |
| VA | `va_2024_gen_prec.zip` | 03/16/26 | Virginia Department of Elections, Historic Elections Database |
| VT | `vt_2024_gen_prec.zip` | 02/17/26 | Vermont Secretary of State |
| WA | `wa_2024_gen_prec.zip` | 05/21/25 | Washington Secretary of State |
| WI | `wi_2024_gen_prec.zip` | 07/02/2025 | Wisconsin State Legislature (ward-level results) |
| WV | `wv_2024_gen_prec.zip` | 2/17/26 | West Virginia Secretary of State |
| WY | `wy_2024_gen_prec.zip` | 4/28/26 | Wyoming Secretary of State |

## 2. The New York Times: 2024 precinct results (DC only)

- **What:** `precincts-with-results.topojson.gz`, the national precinct file (127,270 precincts in 45 states). Only the 144 DC rows are used; every other state comes from RDH. The first read takes about 2.5 minutes, so DC is cached in `data/interim/nyt_dc_precincts.gpkg`.
- **Title and publisher:** "Presidential precinct data for the 2024 U.S. general election", The New York Times. Repository: https://github.com/nytimes/presidential-precinct-map-2024. Contact: electionsdata@nytimes.com. The README credits a named map team and about 40 further contributors.
- **Download location:** the README lists the national files under `https://int.nyt.com/newsgraphics/elections/map-data/2024/national/` (as reported from the README; not re-checked). This copy was accessed on or before 2026-10-28; where it was downloaded from is not recorded. The local file's timestamp is March 22, 2025, while the repository's commit history runs to January 2026 and the README gives no publication date or version.
- **Requested citation (from the README):** "2024 Precinct-Level Election Results." *New York Times*, www.nytimes.com/interactive/2025/us/elections/2024-election-map-precinct-results.html. Accessed on or before 2026-10-28. The README also asks users to link to the published map at https://www.nytimes.com/interactive/2025/us/elections/2024-election-map-precinct-results.html.
- **License:** NYT Computational Use of Data Agreement v1.0 - Non-Commercial. In summary: computational use, credit to The New York Times required, non-commercial use only (with an exception for editorial use by journalists), and redistribution only with attribution kept and recipients bound by the same terms. **Check that this fits your intended use.**
- **Fields:** `state`, `GEOID` (county FIPS plus precinct name), `votes_dem` (Harris), `votes_rep` (Trump), `votes_total` (includes third-party and write-in votes when the source reports them), `pct_dem_lead`, `official_boundary` (true when the shape came from a state or county file; true for all 144 DC precincts). The file also has an `id` field the README does not document. No CRS is stated; the DC coordinates are longitude/latitude, so EPSG:4326 is assumed (verified on load).
- **DC check:** Harris 294,185, Trump 21,076 and total 325,869 equal the FEC figures exactly, so "other" derived as `votes_total - votes_dem - votes_rep` is 10,608, also equal to the FEC.

## 3. U.S. Census Bureau: TIGER/Line 2021 block groups

- **What:** `tl_2021_{statefp}_bg.zip` (vintage 2021), with `GEOID`, `ALAND` and `AWATER`. Used for the allocation targets and for each block group's land fraction. Only the 50 states and DC are used, because those are the jurisdictions with voting results. The folder also holds files for American Samoa, Guam and the Northern Mariana Islands (FIPS 60, 66, 69); they are ignored.
- **Vintage history:** the pipeline first ran on TIGER/Line 2024 block groups. On 2026-11-07, after those files were replaced with the 2021 set, all 51 outputs were rebuilt. For every state except Connecticut, every block group ID in the earlier outputs also exists in the 2021 file (boundaries were not compared). Connecticut's IDs differ completely between the two vintages (none of the 2,711 matched), probably because newer Census geography replaced Connecticut's counties with planning regions; this is not verified. The 2021 Connecticut IDs use the eight historical county codes (001 to 015), so they will not join to Census products that use planning regions.
- **Publisher:** U.S. Department of Commerce, U.S. Census Bureau, Geography Division. Each zip holds ISO 19115 metadata (`.shp.iso.xml`) titled, for Rhode Island, "TIGER/Line Shapefile, 2021, state, Rhode Island, Current Block Group State-based". It gives the Census download location, http://www2.census.gov/geo/tiger/TIGER2021/BG/tl_2021_44_bg.zip (pattern `.../TIGER2021/BG/tl_2021_{fips}_bg.zip`). Datum NAD83 (EPSG:4269). Dates in the metadata include 2021 and 20210523.
- **Date accessed / download location:** accessed on or before 2026-11-07 (the date the pipeline was re-run on these files). The Census location above comes from the metadata; where this copy was actually downloaded from is not recorded.
- **Citation:** built from the file metadata, not an official Census string: U.S. Census Bureau, Geography Division. *TIGER/Line Shapefile, 2021, state, {State}, Current Block Group State-based* (`tl_2021_{fips}_bg`). Accessed on or before 2026-11-07.
- **License / terms:** public domain under 17 U.S.C. § 105 (U.S. government work), as stated by the project owner. The 2021 metadata also says the TIGER/Line Shapefile products are not copyrighted, while "TIGER/Line" and "Census TIGER" are registered trademarks of the Census Bureau.

## 4. Federal Election Commission: official 2024 presidential results

- **What:** `Federal Election Commission, Official 2024 Presidential General Election Results.csv`, state totals for Harris, Trump and "All other", plus a "U.S. total" row. Used only to validate the precinct data; it does not feed the output.
- **Citation (as supplied):** Federal Election Commission, Official 2024 Presidential General Election Results, compiled from state election offices, January 16, 2025. Harris figures are from page 3, Trump from page 5, and total votes from page 6. PDF: https://www.fec.gov/documents/5644/2024presgeresults.pdf.
- **Note on "All other":** it is not one of the cited PDF figures. It is consistent with total minus Harris minus Trump (checked for DC), but how the CSV column was produced is not documented.
- **Date accessed:** on or before 2026-10-28. **License / terms:** public domain under 17 U.S.C. § 105 (U.S. government work), as stated by the project owner; the file itself does not state a license.

## Using the outputs

The block group files in `data/processed/` are derived from RDH (50 states) and NYT (DC), so both sources' terms carry over. In summary, and subject to the checks noted above:

- **Non-commercial only.** RDH limits use to noncommercial, nonpartisan purposes, and the NYT license is non-commercial (with an editorial exception for journalists). The Census and FEC inputs are public domain and add no restriction.
- **Credit both.** Credit RDH using its suggested wording, and cite the NYT map as requested, wherever the outputs or anything computed from them are published or shared.
- **Sharing the files.** RDH allows passing its data, in whole or in part, to others only if they agree to its terms, and the NYT license requires recipients to be bound by its terms. Anyone you give the outputs to should be pointed to both.
- This is a summary of what the sources say, not legal advice. Ask RDH and the NYT if your intended use is unclear.

## How the sources fit together

Precinct votes (RDH, or NYT for DC) are split across block groups (TIGER/Line) by overlapping land area, and each state's precinct totals are checked against the FEC. Among the 50 RDH states, 35 match the FEC exactly on Harris and Trump and the other 15 differ by at most 0.083%; DC (NYT) matches exactly. The "All other" column differs in 18 states and was not investigated. See `CLAUDE.md` for the method and commands.
