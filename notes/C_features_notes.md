# C – Features, selection, PCA, clusters
Numbers below are from `02_feature_engineering.py` and `04_selection_pca_clusters.py` on the full
NFHS-5 file (221,263 children, 707 districts), using A's cleaning from `a/cleaning-missing`.

## 1. Engineered features and why they exist
| Feature | How | Why |
|---|---|---|
| stunted / wasted / underweight (+ severe) | haz / whz / waz < -2 (< -3) | WHO definitions; the outcomes we report |
| overweight | whz > 2 | double-burden check |
| any_failure, n_failures | count of the three above | children with 2+ failures need priority |
| age_group | 0-5, 6-11, 12-23, 24-35, 36-47, 48-59 months | stunting jumps from 25% to 40% after 12 months |
| low_birth_wt | birth weight < 2500 g | early risk factor (42.9% vs 32.7% stunted) |
| bw_recorded | birth weight present (1/0) | missing card is itself a risk signal (45.5% vs 34.5% stunted) |
| multiple_child_mother | mother has 2+ children under 5 | competition for care and food |
| birth_season | month → Winter/Summer/Monsoon/Post-monsoon | seasonal food/infection patterns (small effect: 34.4–36.7%) |
| bmi_proxy | kg / m², only where BAZ is valid | so entry errors (20 cm, 77 kg) don't create absurd BMIs |
| wealth_rank, edu_rank | ordered 1–5, 0–3 | lets us use them as numbers in correlation |
| is_poorest, mom_no_edu, is_rural | 1/0 indicators | to build survey-weighted district shares |
| dhs_flag_haz/waz/whz/baz | raw code 9996/9997/9998 | DHS's own "implausible measurement" flags (cleaning turns them into NaN, so we read them back from the raw file) |
| implausible_any | any of the flags above | **data-quality feature**: entry/measurement error, kept separate from plain missing (9999) – this is our problem statement |
| haz_missing | no usable HAZ | missing for any reason |

**National check (survey-weighted):** stunting **35.5%**, wasting **19.2%**, underweight **32.1%** –
identical to the official NFHS-5 report, so cleaning + weights are correct. Any failure 52.9%.
Implausible (DHS-flagged): **6.91%** of children. HAZ missing: **8.0%**.

## 2. Leakage
haz, waz, whz, height and weight are not used to predict stunting: stunting *is* haz < -2, so the model
would just read the answer. We use only things known before the child is measured.

## 3. Why AUC = 0.652 is an honest finding
Random forest on background factors only gives AUC 0.652 (0.5 = coin toss, 1 = perfect).
Background factors shift the *risk* but do not decide each child – B's chart 10 shows the whole height
distribution moves left for poor children. So child-level prediction is weak, but group/district
targeting works, which is why we cluster districts.
Top features by mutual information: birth order index (mostly a proxy for the child's age – younger
siblings are measured younger, before stunting builds up), birth weight recorded, mother's education,
sex, mother with several under-5 children, caste, wealth. All MI values are small (< 0.025): no single
factor dominates.

## 4. PCA
**Child level – four z-scores only (haz, waz, whz, baz).** Raw height/weight were dropped: they mainly
measure age. The z-scores overlap (B's chart 06: whz–baz 0.97), so PCA compresses them:

| | PC1 (61.3%) | PC2 (38.1%) |
|---|---|---|
| haz | -0.04 | **0.81** |
| waz | 0.49 | 0.53 |
| whz | **0.62** | -0.15 |
| baz | **0.61** | -0.22 |

- PC1 = **thinness** (acute undernutrition: wasting).
- PC2 = **shortness** (chronic undernutrition: stunting).
- 2 PCs explain **99.3%** → four scores are really two dimensions.
- haz barely loads on PC1 (-0.04): **stunting and wasting are almost independent problems** – a child can
  be short without being thin and vice versa, so programmes must screen for both.

When PCA would not suit: categorical data (caste, state), non-linear patterns, or when a decision-maker
needs one original variable explained.

**District level.** 7 standardised, survey-weighted indicators; kept **4 PCs = 86.7%** of variance.
- PC1 – all loadings positive (stunting 0.44, underweight 0.48, % poorest 0.43, % mother no edu 0.41)
  → **"overall deprivation" axis**.
- PC2 – wasting (+0.45) and low birth weight (+0.52) high, but poverty (-0.34) and rurality (-0.51) low
  → **acute problems in less poor / more urban districts**.
Clusters are formed on these 4 PCs.

## 5. Choosing k (figure 15_choose_k, choose_k_metrics.csv)
| k | silhouette | Davies-Bouldin | stability (ARI) | smallest cluster |
|---|---|---|---|---|
| 2 | **0.302** | 1.237 | 1.000 | 299 |
| 3 | 0.223 | 1.497 | 0.959 | 175 |
| **4** | 0.214 | 1.398 | 0.935 | **154** |
| 5 | 0.224 | 1.346 | 0.969 | 69 |
| 6 | 0.214 | 1.286 | 0.905 | 62 |

- Elbow: inertia falls smoothly, no sharp bend.
- Silhouette is best at k = 2, then flat (0.21–0.22) for k = 3…10.
- **Decision: k = 4.** k = 2 only splits "high vs low burden", which gives no different actions.
  For k ≥ 3 the metrics are nearly tied, so we chose the k that is stable (ARI 0.935), keeps every
  cluster large (≥ 154 districts) and gives four profiles that each need a *different* action.
  k = 5 was checked: similar silhouette but one cluster shrinks to 69 districts.
- **Honest limit:** silhouette ≈ 0.21 means districts form a continuum, not naturally separate groups.
  The clusters are *profiles for targeting*, not hard categories.

## 6. Cluster profiles (cluster_profile.csv, 1 = lowest stunting; mean of district %)
| Cluster | Districts | Stunting | Wasting | Underweight | Low BW | % poorest | % mother no edu | % rural | Implausible % | HAZ missing % |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 164 | 27.9 | 14.1 | 22.4 | 18.8 | 3.5 | 8.7 | 50.3 | 6.0 | 8.9 |
| 2 | 156 | 28.6 | 14.1 | 20.1 | 11.6 | 19.4 | 13.2 | 83.0 | 6.6 | 5.7 |
| 3 | 228 | 33.8 | **23.0** | 34.2 | 17.2 | 21.0 | 15.2 | 77.6 | **8.1** | 7.8 |
| 4 | 159 | **43.9** | 21.1 | **39.4** | 18.5 | **47.7** | **35.8** | **89.0** | 7.4 | 6.5 |

| Cluster | Name | Action |
|---|---|---|
| 1 | Better-off but not safe | Low poverty yet 28% stunted and the highest low birth weight → maternal nutrition and antenatal care |
| 2 | Rural, moderate burden | Lowest low birth weight; keep routine anganwadi growth monitoring |
| 3 | Acute hotspot (largest group) | Highest wasting (23%) → screening and treatment of severe wasting, supplementary feeding |
| 4 | Deep deprivation | Half the children in the poorest quintile, 36% of mothers with no schooling, 44% stunted → combined poverty, education and nutrition support |

**District-level correlation:** stunting vs % mothers with no education, Spearman **0.54**.

**Data quality per cluster:**
- Flagged (implausible) measurements are spread across all clusters (6.0–8.1%); district stunting vs
  implausible % Spearman = **0.08**, so errors are *not* what drives the high-burden map.
- Cluster 3, the wasting hotspot, has the most flagged records (8.1%). Wasting uses weight-for-height,
  the most-flagged measurement, so its wasting figure needs the most careful re-measurement.
- HAZ missing is highest in the best-off cluster 1 (8.9%), matching A's finding that richer children are
  more often unmeasured → prevalence in better-off districts is less certain.

## 7. Limits
No districts dropped (all 707 had ≥ 30 children). Clusters show associations, not causes.
District shares are survey-weighted; the random forest and PCA are unweighted.
