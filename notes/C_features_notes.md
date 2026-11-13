# C – Features, selection, PCA, clusters
Fill every `___` from the printout of `02_feature_engineering.py` and `04_selection_pca_clusters.py`
after re-running on A's final cleaned file.

## 1. Engineered features and why they exist
| Feature | How | Why |
|---|---|---|
| stunted / wasted / underweight (+ severe) | haz / whz / waz < -2 (< -3) | WHO definitions; the outcomes we report |
| overweight | whz > 2 | double burden check |
| any_failure, n_failures | count of the three above | children with 2+ failures need priority |
| age_group | 0-5, 6-11, 12-23, 24-35, 36-47, 48-59 months | B's chart shows the gap opens after 12 months |
| low_birth_wt | birth weight < 2500 g | known early risk factor |
| bw_recorded | birth weight present (1/0) | missing card often means home birth / less care access |
| multiple_child_mother | mother has 2+ children under 5 | competition for care and food |
| birth_season | month -> Winter/Summer/Monsoon/Post-monsoon | seasonal food and infection patterns |
| bmi_proxy | kg / m², only where BAZ passed the WHO screen | so entry errors (20 cm, 77 kg) don't create absurd BMIs |
| wealth_rank, edu_rank | ordered 1–5, 0–3 | lets us use them as numbers in correlation |
| is_poorest, mom_no_edu, is_rural | 1/0 indicators | to build survey-weighted district shares |
| implausible_any, haz_missing | failed WHO screen / no usable HAZ | **data-quality features** – link to our problem statement (entry errors vs real risk) |

National check (weighted): stunting ___% (official NFHS-5: 35.5%), implausible ___%, HAZ missing ___%.

## 2. Leakage
haz, waz, whz, height and weight are not used to predict stunting: stunting *is* haz < -2, so the model
would just read the answer. We only use things known before measuring the child.

## 3. Why AUC ≈ ___ is an honest finding
Background factors (wealth, education, state, age, birth weight) shift the *risk* but do not decide each child.
B's chart 10 shows the whole height distribution shifts for poor children – it is a population-level effect,
so a child-level classifier cannot be very sharp. This supports targeting **groups and districts**, which is
why we cluster districts next. Top features (RF / mutual information): ___, ___, ___.

## 4. PCA
**Child level – z-scores only (haz, waz, whz, baz).** Raw height/weight were dropped from the block because
they mainly measure age. The z-scores are strongly correlated (B's chart 06: whz–baz 0.97), so PCA compresses them:
- PC1 (___%): all four load positively → overall nutritional status.
- PC2 (___%): haz vs whz/baz with opposite signs → *chronic* (short) vs *acute* (thin) undernutrition.
- 2 PCs explain ___% → 4 overlapping scores are really ~2 dimensions.
When PCA would not suit: categorical data (caste, state), non-linear patterns, or when we need to explain
a single original variable to a decision-maker.

**District level.** 7 standardised, survey-weighted district indicators (stunting, wasting, underweight,
low birth weight, % poorest, % mothers with no education, % rural). Kept ___ PCs (≥ 80% variance).
PC1 loads on ___ → name it "___". Clusters are run on these PCs.

## 5. Choosing k (figure 15_choose_k, table choose_k_metrics.csv)
Tested k = 2..10 with elbow (inertia), silhouette, Davies-Bouldin and stability (mean ARI across 10 random seeds).
- Elbow bend around k = ___.
- Silhouette best at k = ___ (value ___); at k = 4 it is ___.
- Stability at k = 4: ARI ___ (1.0 = same clusters every run).
- **Decision: k = ___** because ___ (metric evidence + each cluster leads to a different action;
  smallest cluster still has ___ districts).
Be honest if silhouette is low (< 0.25): districts form a continuum, so clusters are *useful profiles for
targeting*, not natural separate groups.

## 6. Cluster profiles (cluster_profile.csv, 1 = lowest stunting)
| Cluster | Districts | Stunting | Wasting | % poorest | % mother no edu | Implausible % | Name | Action |
|---|---|---|---|---|---|---|---|---|
| 1 | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ |
| 2 | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ |
| 3 | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ |
| 4 | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ |

Data quality: does any cluster also have higher implausible / missing %? (Spearman stunting vs implausible = ___.)
If yes: those districts need better measurement *and* nutrition support – this is our problem statement's point.

## 7. Limits
Districts with < 30 children dropped (___ districts). Clusters describe associations, not causes.
District shares are survey-weighted; the RF and PCA are unweighted.
