# blockgroupvoting2024

## 2024 General Election Voting by US Census Block Group

#### PROBLEM AND OPPORTUNITY 

In the United States, voting is largely a private matter. A registered voter is given a randomized ballot form or machine to prevent linkage between their voting choices and their identity. This disconnect supports confidence in the election process, but it provides obstacles to an election's analysis. A common solution is to field exit polls, interviewing voters immediately after leaving their polling location. This method is rife with bias, however, and functionally limited in direct demographics data collected. People may be selected with bias, and they may respond less than truthfully when they share their voting decision and personal information.

Following the 2016 general election, though, most states published their election results for each voting precinct. These publications were additionally supported by the geographical areas assigned to each precinct. While precincts have few demographic traits directly, their geographies have characteristics that make them projectable onto U.S. Census geographies. Both voting precincts and U.S. Census block groups:
 * are exclusive,
 * do not overlap,
 * are adjacent,
 * fully cover their corresponding state and county
 * and have roughly the same land area in size. 

As a result, geographic processing can now be applied to project precinct election results onto US Census block groups. Analytically, a projection of local demographics does not allow conclusions about voters themselves. However, the dataset does allow statements related to the demographics that yield voting behavior. The dataset that results from this programming provides voting results allocated by Census block groups. The block group identifier can be joined to Census Decennial and American Community Survey demographic estimates. 

Complete documentation and the programming to reproduce these results can be found here https://github.com/OpenEnvironments/blockgroupvoting2020.

#### DATA SOURCES 

This projection relies on 4 major data sources.
 * The geographic shapefiles for blockgroups are taken from U.S. Census Bureau TIGER/Line 2024 publications which provide a file for each state.  The 2024 publication relies on the boundary definitions set during the decennial census in 2020.
 * All except Washington, DC election results were taken from Redistricting Data Hub at https://redistrictingdatahub.org/. Similarly, voting precinct results are available there with the precinct boundaries.
 * Washington, DC's 2024 election results were taken from the New York Times publication https://github.com/nytimes/presidential-precinct-map-2024.
 * Finally, precinct level voting results were aggregated to test completeness against the state totals published by the US Federal Election Commission (FEC) here https://www.fec.gov/introduction-campaign-finance/election-results-and-voting-information/

While not directly involved, this work is informed by a similar effort in 2022 shared on Harvard's dataverse platform "2020 General Election Voting by US Census Block Group". https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/NKNWBX

More detail on each of these sources can be found in the markdown file named DATA_SOURCES.md kept in the project's version control repository here https://github.com/OpenEnvironments/blockgroupvoting2024.

State voting precincts lie within state and county boundaries. The Census Bureau, on the other hand, publishes its estimates across a variety of geographic definitions including a hierarchy of states, counties, census tracts and block groups. Their definitions can be found in the Census TIGER\Line publications. The lowest level of this geography changes often and can obsolesce before the next census survey (Decennial or American Community Survey programs). The second to lowest census level, block groups, have the benefit of both granularity and stability however. The 2020 Decennial survey details US demographics into 217,740 block groups each with between a few hundred and a few thousand people. 

#### DATA DICTIONARY

**Note: the precinct votes are allocated based on proportions, so the results are decimals rather than integers**
The publication's dataset columns include:

| Column | Data Type | Description |
| :--- | :---: | ---: |
| GEOID | String | 12 digit primary key, Census GEOID of the block group concatenates FIPS: 2 digit state 3 digit county within state 6 digit Tract identifier 1 digit Block Group identifier |
| REP | Float |Votes for Republican party candidate for president |
| DEM | Float | Votes for Democratic party candidate for president |
| OTH | Float | Votes for candidates other then Repubican or Democrat affiliation|
| TOT | Float | Total votes for presidential candidates regardless of party |
| STATE | String | 2 character abbreviation for the US State involved |
| PRECINCTS | Integer | Number of voting precincts that overlay this block group |

#### METHODS

The projection follows these serial steps.
1. Open four datasets: Census block group shapes, voting results from Redistricting Data Hub, voting results for DC from the New York Times, and the state level total voting from the Federal Election Commission.
2. Test the data to confirm
    - precinct level totals aggregate to the state level totals from the FEC
    - precinct geographies fully overlay block groups
    - data quality and nullability checks
3. For each block group,
    - find the precincts that overlay it.
    - attribute the voting results from each of those precincts to the blockgroup based on the proportion of the precincts land that lies in that block group.
4. Evaluate the results based on
    - univariate distributions, notable outliers
    - bivariate relationships to block group demographic data
    - changes from the 2020 vintage publication

#### ASSUMPTIONS, NOTES AND CONCERNS
 * Voting results are attributed based on proportion of shared geographic area. This assumes that people live uniformly across land. For example, a block group where many people live in the north east corner will be biased to reflect precincts along its more sparse areas.
 * Vote counting practices vary by state, especially regarding mail-in, provisional and absentee ballots which may be processed at the state, county or parish level. See the New York Times discussion here https://github.com/nytimes/presidential-precinct-map-2024#state-by-state-data-and-caveats
 * Blocks groups include area that is covered by water. Block group that are entirely water are given Block Group '0' and have no population to attribute votes to. Votes are attributed based on land area only.
 * The ACS is used to source demographics. It uses annual sampling to update the decennial census. These incremental adjustments are more accurate the nearer the sampling is done to the decennial. When the 2020 and 2024 election results are compared, part of the voting shifts are due to demographic changes rather than population, turnout or party affiliation.
 * The block group shapes change only very slightly over years. In 2022, for example, Connecticut renovated its block group definitions to change from counties to planning districts. The underlying shapes didn't change, but aggregating to the county equivalent level will need a mapping for Connecticut. Some shapes also change with shifts in waterways and shore lines.

#### RECOGNITION, CITATIONS 

A special thanks to Redistricting Data Hub at redistrictingdatahub.org for their collation and technical support on their voting data.

**Precinct level voting results**

        Redistricting Data Hub. (n.d.). [State] 2024 general election precinct boundaries and election results [Data set]. https://redistrictingdatahub.org/data/about-our-data/precinct-boundaries-and-election-results/

        The New York Times. (n.d.). 2024 precinct-level election results [Data set]. https://github.com/nytimes/presidential-precinct-map-2024

**US Census block group geographies**

        U.S. Census Bureau. (2021). TIGER/Line shapefile, 2021, state, [State], current block group state-based [Data set]. https://www2.census.gov/geo/tiger/TIGER2021/BG/
        
**FEC totals by state**

        Federal Election Commission. (2025, January 16). Official 2024 presidential general election results. https://www.fec.gov/documents/5644/2024presgeresults.pdf


#### LICENSE

This code is available subject to the Creative Commons Open Source License CC0 1.0.

Attribution is requested but not required.

#### SUMMARY STATISTICS


| State | Harris | Trump | Other | Total | % vs FEC | 
| :--- | ---: | ---: | ---: | ---: | ---: |
| AK | 140,026 | 184,458 | 13,693 | 338,177 | 0.000% | 
| AL | 772,412 | 1,462,616 | 30,062 | 2,265,090 | 0.000% | 
| AR | 396,905 | 759,241 | 26,530 | 1,182,676 | 0.000% | 
| AZ | 1,582,860 | 1,770,242 | 36,217 | 3,389,319 | −0.025% | 
| CA | 9,273,042 | 6,077,541 | 504,479 | 15,855,062 | −0.066% | 
| CO | 1,728,159 | 1,377,441 | 87,145 | 3,192,745 | 0.000% | 
| CT | 992,053 | 736,918 | 30,039 | 1,759,010 | 0.000% | 
| DC | 294,185 | 21,076 | 10,608 | 325,869 | 0.000% | 
| DE | 289,758 | 214,351 | 7,588 | 511,697 | −0.237% | 
| FL | 4,683,038 | 6,110,126 | 100,384 | 10,893,548 | −0.002% | 
| GA | 2,548,017 | 2,663,117 | 38,932 | 5,250,066 | −0.016% | 
| HI | 313,044 | 193,661 | 9,996 | 516,701 | 0.000% | 
| IA | 707,278 | 927,019 | 29,209 | 1,663,506 | 0.000% | 
| ID | 274,972 | 605,246 | 24,839 | 905,057 | 0.000% | 
| IL | 3,062,863 | 2,449,079 | 137,682 | 5,649,624 | +0.290% | 
| IN | 1,163,655 | 1,720,301 | 55,068 | 2,939,024 | +0.080% | 
| KS | 544,853 | 758,802 | 23,936 | 1,327,591 | 0.000% | 
| KY | 704,043 | 1,337,491 | 32,993 | 2,074,527 | 0.000% | 
| LA | 766,870 | 1,208,505 | 31,600 | 2,006,975 | 0.000% | 
| MA | 2,126,518 | 1,251,303 | 95,847 | 3,473,668 | 0.000% | 
| MD | 1,902,577 | 1,035,550 | 100,207 | 3,038,334 | 0.000% | 
| ME | 435,645 | 377,976 | 17,745 | 831,366 | −0.001% | 
| MI | 2,736,438 | 2,816,346 | 110,293 | 5,663,077 | −0.020% | 
| MN | 1,656,979 | 1,519,032 | 77,909 | 3,253,920 | 0.000% | 
| MO | 1,200,599 | 1,751,986 | 42,742 | 2,995,327 | 0.000% | 
| MS | 466,667 | 747,744 | 13,596 | 1,228,007 | 0.000% | 
| MT | 231,906 | 352,079 | 18,978 | 602,963 | −0.004% | 
| NC | 2,713,609 | 2,896,941 | 85,832 | 5,696,382 | −0.048% | 
| ND | 112,327 | 246,505 | 9,323 | 368,155 | 0.000% | 
| NE | 369,995 | 564,816 | 12,348 | 947,159 | −0.528% | 
| NH | 418,488 | 395,523 | 12,178 | 826,189 | 0.000% | 
| NJ | 2,220,713 | 1,968,215 | 83,797 | 4,272,725 | 0.000% | 
| NM | 478,755 | 423,381 | 7,557 | 909,693 | −1.485% | 
| NV | 705,028 | 750,923 | 28,431 | 1,484,382 | −0.031% | 
| NY | 4,619,551 | 3,579,514 | 105,931 | 8,304,996 | +0.514% | 
| OH | 2,533,699 | 3,180,116 | 51,202 | 5,765,017 | −0.048% | 
| OK | 499,599 | 1,036,213 | 30,361 | 1,566,173 | 0.000% | 
| OR | 1,240,600 | 919,480 | 84,413 | 2,244,493 | 0.000% | 
| PA | 3,423,042 | 3,543,308 | 67,856 | 7,034,206 | −0.347% | 
| RI | 285,132 | 214,398 | 13,824 | 513,354 | −0.006% | 
| SC | 1,028,452 | 1,483,747 | 35,941 | 2,548,140 | 0.000% | 
| SD | 146,811 | 271,938 | 9,979 | 428,728 | −0.045% | 
| TN | 1,056,265 | 1,966,865 | 40,812 | 3,063,942 | 0.000% | 
| TX | 4,835,134 | 6,393,403 | 175,991 | 11,404,528 | +0.139% | 
| UT | 562,223 | 883,082 | 42,486 | 1,487,791 | −0.047% | 
| VA | 2,333,778 | 2,074,097 | 95,413 | 4,503,288 | 0.000% | 
| VT | 235,791 | 119,395 | 14,236 | 369,422 | 0.000% | 
| WA | 2,245,849 | 1,530,923 | 147,471 | 3,924,243 | 0.000% | 
| WI | 1,668,229 | 1,697,626 | 57,063 | 3,422,918 | 0.000% | 
| WV | 214,309 | 533,556 | 14,525 | 762,390 | −0.025% | 
| WY | 69,527 | 192,633 | 6,888 | 269,048 | 0.000% | 
| US | 75,012,268 | 77,295,845 | 2,942,175 | 155,250,288 | +0.008% |   | 






