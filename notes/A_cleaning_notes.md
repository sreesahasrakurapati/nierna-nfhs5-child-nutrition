# A – Cleaning decisions log

### 1. Special codes → NaN

- **What we did:** Replaced the identified DHS special codes with missing values (`NaN`) in the relevant measurement and z-score variables.
- **Why:** These codes represent missing or unavailable measurements, not actual numerical measurements. Keeping them as numbers would distort summaries, distributions and anomaly detection.
- **Alternative:** Keep the special codes as numeric values or delete the affected child records. We chose to retain the records and mark only the affected values as missing.

### 2. Unit fixes

- **What we did:** Converted the DHS-stored measurement values into readable units for z-scores, weight, height, birth weight and sample weights.
- **Why:** The raw data use scaled values. Conversion is necessary for meaningful interpretation and analysis.
- **Alternative:** Keep the original scaled values throughout the analysis. We converted them during cleaning while retaining the child records.

### 3. WHO plausibility limits

- **What we did:** Applied screening limits to identify implausible z-scores: HAZ (-6 to +6), WAZ (-6 to +5), WHZ (-5 to +5) and BAZ (-5 to +5).
- **Why:** Values outside these limits may indicate measurement or recording problems and should not be treated as ordinary growth measurements.
- **Alternative:** Keep all values without screening or remove entire child records. We screened the affected z-score values instead.
- **Audit result:** No values outside these limits remained in the cleaned z-score variables. These are screening thresholds and should be described as such.

### 4. Dropped columns

- **What we did:** Removed columns not required for the agreed analysis, including `b5`, `int_day2`, `dob_cmc`, `household`, `mother_line`, `cluster`, `v021` and `bidx`.
- **Why:** This reduces unnecessary columns while retaining the variables needed for the cleaning and analysis workflow.
- **Alternative:** Keep every raw column. We retained the columns needed for the project workflow.

### 5. Caste blanks → "Not recorded"

- **What we did:** Replaced missing caste entries with the category "Not recorded".
- **Why:** This makes missing category information explicit and avoids treating it as a genuine caste group.
- **Alternative:** Delete records with missing caste or leave them as blank values. We retained the records and labelled the missing category.

### 6. Missing z-scores by state and wealth

- **What we did:** Compared survey-weighted missingness percentages for HAZ, WAZ and WHZ across states and wealth quintiles.
- **Why:** Missing measurements may not be distributed equally across population groups. This can affect the interpretation of the analysis.
- **Findings:**
  - Sikkim (state code 11) had the highest missingness among the displayed state results: HAZ 18.42%, WAZ 16.87% and WHZ 27.21%.
  - Telangana (state code 36) also showed relatively high missingness: HAZ 14.44%, WAZ 11.38% and WHZ 17.14%.
  - The richest wealth quintile had higher missingness than the other wealth groups: HAZ 11.57%, WAZ 9.48% and WHZ 13.54%.
- **Alternative:** Assume missingness is equal across groups or remove all records with missing z-scores. We compared groups and retained records with missing measurements.
- **Interpretation:** Missingness varies across groups. These are descriptive associations and do not establish why measurements are missing.

### 7. NFHS-5 state-code mapping verification

- **What we did:** Inspected the metadata of the original NFHS-5 `IAKR7EFL.DTA` file using Python and verified the value labels for `v024`.
- **Why:** The cleaned dataset initially contained numeric `state_code` values but no state-name column. The EDA script expected a column named `state`, causing a `KeyError`.
- **Verified findings:**
  - The original DHS metadata provides 36 distinct state/UT codes.
  - Code 25 represents Dadra & Nagar Haveli and Daman & Diu together.
  - Code 26 is absent from this NFHS-5 mapping.
  - Code 29 represents Karnataka.
  - Code 11 represents Sikkim.
  - Code 36 represents Telangana.
  - Code 37 represents Ladakh.
- **Next step:** Add a verified `state` column using the original DHS value labels while retaining the numeric `state_code` column.
- **Alternative:** Use an unofficial mapping or display only numeric state codes. We used the original NFHS-5 metadata to avoid incorrect state names.

### Initial data audit

- Raw dataset: 221,263 child records and 33 columns.
- Exact duplicate rows: 0.
- Unique case IDs: 172,421 (case IDs are not child counts).
- Unique districts: 707.
- Cleaned dataset before adding the state-name column: 221,263 rows and 30 columns.
- Missing values after cleaning:
  - HAZ: 6.89%
  - WAZ: 4.85%
  - WHZ: 8.85%
  - BAZ: 8.61%
  - Weight: 4.27%
  - Height: 4.56%
  - Birth weight: 9.38%

### Key results for presentation

1. The dataset contained 221,263 child records and no exact duplicate rows.
2. DHS special codes were handled as missing values rather than valid measurements.
3. Measurement units and z-score screening were addressed during cleaning.
4. Missingness differed across states and wealth groups.
5. The original NFHS-5 metadata was used to verify the state-code mapping.

### Anthropometric variable names

The original DHS variable codes were converted into meaningful names for easier understanding and analysis.

| Cleaned name | Meaning |
|---|---|
| `haz` | Height-for-Age Z-score (stunting indicator) |
| `waz` | Weight-for-Age Z-score (underweight indicator) |
| `whz` | Weight-for-Height Z-score (wasting indicator) |
| `baz` | BMI-for-Age Z-score |

Short standard names were retained in the dataset and code, while their full meanings are documented for interpretation.