# Data dictionary (raw DHS code -> our name)

| Raw | Our name | Meaning / note |
|---|---|---|
| caseid | caseid | mother+household id (siblings share it) |
| v024 | state_code / state | state (verify names vs DHS codebook) |
| sdist | district_code | district |
| v025 | residence | 1 Urban, 2 Rural |
| b4 | sex | 1 Male, 2 Female |
| b1 / b2 | birth_month / birth_year | |
| hw1 | age_months | 0–59 |
| hw2 / hw3 | weight_kg / height_cm | stored x10; 9990+ = flagged/missing |
| hw70 | haz | height-for-age z (x100) -> stunting if < -2 |
| hw71 | waz | weight-for-age z (x100) -> underweight if < -2 |
| hw72 | whz | weight-for-height z (x100) -> wasting if < -2 |
| hw73 | baz | BMI-for-age z (x100) |
| hw13 | measure_status | 0 = measured |
| v106 | mother_edu | 0 None, 1 Primary, 2 Secondary, 3 Higher |
| v190 | wealth_quintile | 1 Poorest … 5 Richest |
| m19 | birth_weight_g | 9996 not weighed, 9998 don't know |
| s116 | caste | 1 SC, 2 ST, 3 OBC, 4 None/General, 8 DK |
| v005 | sample_wt | divide by 1,000,000 |
| midx | birth_order_idx | child's index within mother's file |

## Engineered features (02_feature_engineering.py)
stunted, severe_stunt, wasted, severe_wasted, underweight, overweight, any_failure, n_failures,
age_group, low_birth_wt, bw_recorded, multiple_child_mother, birth_season, bmi_proxy, wealth_rank, edu_rank.
