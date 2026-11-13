
"""PERSON A - Data quality and cleaning.
Input: data/raw/nfhs5_NIEnarya.csv
Output: data/processed/nfhs5_clean.csv

Keep all DHS child-level outputs private.
"""
from common import *

# ---- 1. Load and rename ----
raw = pd.read_csv(RAW)

RENAME = {
    "v024": "state_code", "v025": "residence",
    "sdist": "district_code", "v001": "cluster",
    "v002": "household", "v003": "mother_line",
    "midx": "birth_order_idx", "b4": "sex",
    "b1": "birth_month", "b2": "birth_year",
    "b3": "dob_cmc", "hw1": "age_months",
    "hw2": "weight_kg", "hw3": "height_cm",
    "hw13": "measure_status", "hw15": "height_measure_type",
    "hw16": "int_day", "hw17": "int_day2",
    "hw18": "int_month", "hw19": "int_year",
    "hw70": "haz", "hw71": "waz",
    "hw72": "whz", "hw73": "baz",
    "v106": "mother_edu", "v190": "wealth_quintile",
    "m19": "birth_weight_g", "s116": "caste",
    "v005": "sample_wt"
}

df = raw.rename(columns=RENAME).copy()

# Check required columns
required = [
    "caseid", "state_code", "district_code", "age_months",
    "weight_kg", "height_cm", "measure_status",
    "height_measure_type", "haz", "waz", "whz", "baz",
    "sample_wt", "birth_weight_g"
]
missing_cols = [c for c in required if c not in df.columns]
if missing_cols:
    raise ValueError(f"Missing required columns: {missing_cols}")

# ---- 2. Initial audit ----
print("\nINITIAL DATA AUDIT")
print("Shape:", df.shape)
print("Exact duplicate rows:", df.duplicated().sum())
print("Child records:", len(df))
print("Unique case IDs (not child count):", df["caseid"].nunique())
print("Unique districts:", df["district_code"].nunique())

# Do not delete duplicates automatically.
# caseid can be shared by siblings.

# ---- 3. Special missing codes ----
# These are variable-specific codes observed in the dataset audit.
SPECIAL_CODES = {
    "haz": [9997, 9998, 9999],
    "waz": [9997, 9998, 9999],
    "whz": [9996, 9998, 9999],
    "baz": [9997, 9998, 9999],
    "weight_kg": [9994, 9995, 9996, 9999],
    "height_cm": [9994, 9995, 9996, 9999],
    "birth_weight_g": [9996, 9998]
}

print("\nSPECIAL-CODE AUDIT")
for col, codes in SPECIAL_CODES.items():
    print(col, {code: int((df[col] == code).sum()) for code in codes})

for col, codes in SPECIAL_CODES.items():
    df[col] = df[col].replace(codes, np.nan)

# ---- 4. Unit conversions ----
# DHS anthropometric z-scores have two implied decimal places.
for col in ["haz", "waz", "whz", "baz"]:
    df[col] = df[col] / 100

# Weight and height have one implied decimal place.
df["weight_kg"] = df["weight_kg"] / 10
df["height_cm"] = df["height_cm"] / 10

# DHS sample weight scaling.
df["sample_wt"] = df["sample_wt"] / 1_000_000

# ---- 5. WHO z-score plausibility flags ----
# Flag values outside these commonly used DHS/WHO limits.
# Retain the flags so excluded values can be audited.
LIMITS = {
    "haz": (-6, 6),
    "waz": (-6, 5),
    "whz": (-5, 5),
    "baz": (-5, 5)
}

for col, (lower, upper) in LIMITS.items():
    flag = f"bad_{col}"
    df[flag] = (
        df[col].notna()
        & ~df[col].between(lower, upper)
    )
    df.loc[df[flag], col] = np.nan

print("\nIMPLAUSIBLE Z-SCORE COUNTS")
for col in LIMITS:
    print(col, int(df[f"bad_{col}"].sum()))

# ---- 6. Categorical labels ----
df["sex"] = df["sex"].map({1: "Male", 2: "Female"})
df["residence"] = df["residence"].map({1: "Urban", 2: "Rural"})

df["mother_edu"] = df["mother_edu"].map({
    0: "No education",
    1: "Primary",
    2: "Secondary",
    3: "Higher"
})

df["wealth_quintile"] = df["wealth_quintile"].map({
    1: "Poorest",
    2: "Poorer",
    3: "Middle",
    4: "Richer",
    5: "Richest"
})

df["caste"] = df["caste"].replace({8: np.nan}).map({
    1: "SC",
    2: "ST",
    3: "OBC",
    4: "General/None"
}).fillna("Not recorded")

# HW13: 0 = fully measured; 1 = deceased;
# 2 and above = other reasons for not measuring.
# Keep original numeric status codes.
df["measured"] = (df["measure_status"] == 0).astype("boolean")
df.loc[df["measure_status"].isna(), "measured"] = pd.NA

# Verified NFHS-5 state/UT labels from IAKR7EFL.DTA
STATE_NAMES = {
    1: "Jammu & Kashmir",
    2: "Himachal Pradesh",
    3: "Punjab",
    4: "Chandigarh",
    5: "Uttarakhand",
    6: "Haryana",
    7: "NCT of Delhi",
    8: "Rajasthan",
    9: "Uttar Pradesh",
    10: "Bihar",
    11: "Sikkim",
    12: "Arunachal Pradesh",
    13: "Nagaland",
    14: "Manipur",
    15: "Mizoram",
    16: "Tripura",
    17: "Meghalaya",
    18: "Assam",
    19: "West Bengal",
    20: "Jharkhand",
    21: "Odisha",
    22: "Chhattisgarh",
    23: "Madhya Pradesh",
    24: "Gujarat",
    25: "Dadra & Nagar Haveli and Daman & Diu",
    27: "Maharashtra",
    28: "Andhra Pradesh",
    29: "Karnataka",
    30: "Goa",
    31: "Lakshadweep",
    32: "Kerala",
    33: "Tamil Nadu",
    34: "Puducherry",
    35: "Andaman & Nicobar Islands",
    36: "Telangana",
    37: "Ladakh"
}

df["state"] = df["state_code"].map(STATE_NAMES)

if df["state"].isna().any():
    raise ValueError("Unknown state code found in NFHS-5 data.")

# Keep height_measure_type numeric; do not guess its code labels..

# ---- 7. Drop unnecessary columns ----
df = df.drop(columns=[
    "b5", "int_day2", "dob_cmc", "household",
    "mother_line", "cluster", "v021", "bidx"
], errors="ignore")

# ---- 8. Missingness audit ----
print("\nMISSING VALUES AFTER CLEANING (%)")
missing_pct = (df.isna().mean() * 100).sort_values(ascending=False)
print(missing_pct[missing_pct > 0].round(2))

# Weighted missingness by state and wealth.
df["missing_haz"] = df["haz"].isna().astype(int)
df["missing_waz"] = df["waz"].isna().astype(int)
df["missing_whz"] = df["whz"].isna().astype(int)

def weighted_missing(group, col):
    valid = group["sample_wt"].notna() & (group["sample_wt"] > 0)
    if not valid.any():
        return np.nan
    return np.average(
        group.loc[valid, col],
        weights=group.loc[valid, "sample_wt"]
    ) * 100

for grouping in ["state_code", "wealth_quintile"]:
    print(f"\nWEIGHTED MISSINGNESS BY {grouping.upper()}")
    result = df.groupby(grouping, observed=True).apply(
        lambda g: pd.Series({
            "HAZ missing %": weighted_missing(g, "missing_haz"),
            "WAZ missing %": weighted_missing(g, "missing_waz"),
            "WHZ missing %": weighted_missing(g, "missing_whz")
        }),
        include_groups=False
    )
    print(result.round(2))

df = df.drop(columns=["missing_haz", "missing_waz", "missing_whz"])

# ---- 9. Chart 01: Missingness ----
miss = (df.isna().mean() * 100).sort_values(ascending=False)
miss = miss[miss > 0]

plt.figure(figsize=(8, 5))
sns.barplot(x=miss.values, y=miss.index)
plt.xlabel("Missing values (%)")
plt.title("Missing Values After Cleaning")
save("01_missing")

# ---- 10. Chart 02: Z-score distributions ----
fig, axes = plt.subplots(1, 4, figsize=(15, 3.5))

for ax, col in zip(axes, ["haz", "waz", "whz", "baz"]):
    sns.histplot(df[col].dropna(), bins=60, kde=True, ax=ax)
    ax.axvline(-2, color="red", linestyle="--", label="-2 SD")
    ax.axvline(-3, color="orange", linestyle=":", label="-3 SD")
    ax.set_title(col.upper())
    ax.set_xlabel("Z-score")
    ax.legend()

save("02_zscore_dist")

# ---- 11. Save cleaned data ----
CLEAN.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(CLEAN, index=False)

print("\nCLEANING COMPLETED")
print("Final shape:", df.shape)
print("Saved:", CLEAN)
