# NIErnaya 2026 – Phase 2: Child Malnutrition in India (NFHS-5)

EDA, preprocessing and feature engineering on the NFHS-5 (2019–21) children-under-5 data
(~221k children, 707 districts, 36 states/UTs).

**Story we are testing:** child malnutrition is driven mainly by poverty, mother's education and region,
and children start falling behind after their first birthday.

## Team and ownership
| Member | Owns | Files |
|---|---|---|
| Person A – _name_ | Data quality & cleaning | `src/01_cleaning.py`, `notes/A_cleaning_notes.md` |
| Person B – _name_ | EDA & insights | `src/03_eda.py`, `notes/B_eda_notes.md` |
| Person C – _name_ | Features, selection, PCA, clusters | `src/02_feature_engineering.py`, `src/04_selection_pca_clusters.py`, `notes/C_features_notes.md` |
| Everyone | `src/common.py`, README, final conclusion | agree changes as a group |

## Setup
```bash
git clone <repo-url> && cd nierna-nfhs5-child-nutrition
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# put nfhs5_NIEnarya.csv into data/raw/  (data is NOT in git – get it from the team Drive)
./run_all.sh          # or run the four scripts in src/ one by one
```

## Pipeline
```
data/raw/nfhs5_NIEnarya.csv
   └─ 01_cleaning.py            (A) -> data/processed/nfhs5_clean.csv
        └─ 02_feature_engineering.py (C) -> data/processed/nfhs5_features.csv
             ├─ 03_eda.py                 (B) -> reports/figures/01–06
             └─ 04_selection_pca_clusters.py (C) -> reports/figures/07–08, district_profile.csv
```

## Rules we follow
1. Always use survey weights (`wmean` / `prev` in `common.py`) for any percentage we quote.
2. Special codes (9996/9998/9999) are missing values, never real data.
3. Never use `haz/waz/whz/height/weight` to predict stunting/wasting (leakage).
4. Say "associated with", never "causes".
5. Every chart gets three notes: **pattern → reason → action**.

See `docs/WORKFLOW.md` for the git workflow and `docs/DATA_DICTIONARY.md` for column meanings.
