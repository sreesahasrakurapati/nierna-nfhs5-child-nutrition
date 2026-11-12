# B – EDA notes (DRAFT: reword each cell in your own words before presenting)
For every chart: **Pattern / Reason / Action**. All % are survey-weighted (v005).

| Chart | Pattern | Likely reason (association only) | Action it suggests |
|---|---|---|---|
| 03_age_curve | Mean height-for-age z falls from about -0.6 at birth to about -1.6 by age 2 and stays low. Weight-for-height barely moves. | Complementary feeding and infections in the 2nd year; no data on diet or illness here. | Target nutrition support at 6-24 months. |
| 04_state_stunting | Meghalaya 46.6%, Bihar 42.9%, Jharkhand 39.6% highest; Puducherry 20.1% lowest. | Poverty, low maternal education, access to services differ by state. | Prioritise high-burden states/districts. |
| 05_socio_gradients | Poorest 46% vs richest 23%; no education 46% vs higher 23%; rural 37% vs urban 30%; ST/SC highest. | Wealth, education and caste are entangled. | Target poor households and mothers with little schooling. |
| 06_corr | haz/waz/whz/baz are strongly related (whz-baz 0.97); wealth and education correlate 0.48. | Same body measurements viewed differently. | Do not use both z-scores in a model (redundant and leakage). |
| 09_dist_before_after | Raw data has a spike at 9999 (special codes). Cleaned data are bell-shaped. Birth weight clusters at 2000/2500/3000 g. | Special codes are flags, not data. Birth weight is reported from memory or card and rounded. | Clean first; treat birth weight with caution. |
| 10_haz_by_wealth | The poorest children's whole distribution sits to the left, not just a tail. | Disadvantage affects every child in the group. | Population-level support, not only the worst cases. |
| 11_age_by_wealth | Poor 26% vs rich 20% under 6 months; 51% vs 26% at 12-23 months (24-point gap). | Gap opens after the first birthday. | Reach poor families in the first two years. |
| 12_wealth_by_education | 49% (poor, no education) to 21% (rich, higher). Both effects show within every row and column. | Each adds something independent of the other. | Schooling and income programmes both matter. |
| 13_rural_urban_within_wealth | Within each wealth quintile urban is 0-2 points *higher* than rural, so the overall gap (37% vs 30%) is mostly wealth. | Rural areas simply have more poor households. | Target by wealth, not by rural/urban label. |
| 14_failure_combinations | 47% have no failure, 26% one, 22% two, 5% all three (27% have 2+). | Stunting, wasting and underweight overlap. | Screen for all three at once. |

## Other numbers to quote
- Birth weight: low-birth-weight 42.9% vs 32.7% stunted. Birth weight not recorded: 45.5% vs 34.5% recorded (likely home births / less care access).
- Sex: boys 36.2%, girls 34.6%. Birth season: 34.4-36.7%, small difference.
- Height outliers within age month: 10,796. Kept, as they are real short children.

## Limits to say out loud
Associations, not causes. No data on diet, illness, or feeding. Survey weights used for percentages; histograms and correlations are unweighted.
