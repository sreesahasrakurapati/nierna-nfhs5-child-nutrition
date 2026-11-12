"""PERSON A - data quality & cleaning.  Input: data/raw CSV  ->  Output: data/processed/nfhs5_clean.csv"""
from common import *

raw = pd.read_csv(RAW)
RENAME = {
 "v024":"state_code","v025":"residence","sdist":"district_code","v001":"cluster","v002":"household",
 "v003":"mother_line","midx":"birth_order_idx","b4":"sex","b1":"birth_month","b2":"birth_year","b3":"dob_cmc",
 "hw1":"age_months","hw2":"weight_kg","hw3":"height_cm","hw13":"measure_status","hw15":"height_measure_type",
 "hw16":"int_day","hw17":"int_day2","hw18":"int_month","hw19":"int_year",
 "hw70":"haz","hw71":"waz","hw72":"whz","hw73":"baz",
 "v106":"mother_edu","v190":"wealth_quintile","m19":"birth_weight_g","s116":"caste","v005":"sample_wt"}
df = raw.rename(columns=RENAME).copy()

# ---- audit ----
print(df.shape, "| duplicate rows:", df.duplicated().sum())
print("children:", len(df), "| mothers:", df.caseid.nunique(), "| districts:", df.district_code.nunique())
print("constant columns:", [c for c in df if df[c].nunique() == 1])
for c in ["haz","waz","whz","baz","weight_kg","height_cm","birth_weight_g"]:
    print(f"{c:15s} NaN={df[c].isna().sum():6d}  special codes(>=9990)={(df[c] >= 9990).sum():6d}")

# ---- 1. special codes -> NaN ----
for c in ["haz","waz","whz","baz","weight_kg","height_cm","birth_weight_g"]:
    df.loc[df[c] >= 9990, c] = np.nan
# ---- 2. unit fixes ----
for c in ["haz","waz","whz","baz"]: df[c] = df[c] / 100
df["weight_kg"] = df.weight_kg / 10
df["height_cm"] = df.height_cm / 10
df["sample_wt"] = df.sample_wt / 1e6
# ---- 3. WHO biologically implausible values ----
for col, lo, hi in [("haz",-6,6),("waz",-6,5),("whz",-5,5),("baz",-5,5)]:
    df[f"bad_{col}"] = ~df[col].between(lo, hi) & df[col].notna()
    df.loc[df[f"bad_{col}"], col] = np.nan
# ---- 4. labels / categorical codes ----
df["caste"] = df.caste.replace({8: np.nan})
df["measure_status"] = df.measure_status.replace({9: np.nan})
df["measured"] = (df.measure_status == 0)
df["sex"] = df.sex.map({1:"Male", 2:"Female"})
df["residence"] = df.residence.map({1:"Urban", 2:"Rural"})
df["mother_edu"] = df.mother_edu.map({0:"No education",1:"Primary",2:"Secondary",3:"Higher"})
df["wealth_quintile"] = df.wealth_quintile.map({1:"Poorest",2:"Poorer",3:"Middle",4:"Richer",5:"Richest"})
df["caste"] = df.caste.map({1:"SC",2:"ST",3:"OBC",4:"General/None"}).fillna("Not recorded")
STATE = {1:"Jammu & Kashmir",2:"Himachal Pradesh",3:"Punjab",4:"Chandigarh",5:"Uttarakhand",6:"Haryana",
 7:"Delhi",8:"Rajasthan",9:"Uttar Pradesh",10:"Bihar",11:"Sikkim",12:"Arunachal Pradesh",13:"Nagaland",
 14:"Manipur",15:"Mizoram",16:"Tripura",17:"Meghalaya",18:"Assam",19:"West Bengal",20:"Jharkhand",
 21:"Odisha",22:"Chhattisgarh",23:"Madhya Pradesh",24:"Gujarat",25:"DNH & DD",27:"Maharashtra",
 28:"Andhra Pradesh",29:"Karnataka",30:"Goa",31:"Lakshadweep",32:"Kerala",33:"Tamil Nadu",
 34:"Puducherry",35:"Andaman & Nicobar",36:"Telangana",37:"Ladakh"}   # TODO(A): verify vs DHS codebook
df["state"] = df.state_code.map(STATE)
# ---- 5. drop useless columns ----
df = df.drop(columns=["b5","int_day2","dob_cmc","household","mother_line","cluster","v021","bidx"], errors="ignore")

# ---- quality plots ----
miss = (df.isna().mean()*100).sort_values(ascending=False); miss = miss[miss > 0]
print("Missing % after cleaning:\n", miss.round(1))
plt.figure(figsize=(7,4)); sns.barplot(x=miss.values, y=miss.index, color="#4C72B0")
plt.xlabel("% missing"); plt.title("Missing values after cleaning special codes"); save("01_missing")
fig, ax = plt.subplots(1,4, figsize=(15,3.5))
for a, c in zip(ax, ["haz","waz","whz","baz"]):
    sns.histplot(df[c].dropna(), bins=60, kde=True, ax=a); a.axvline(-2, color="r", ls="--"); a.set_title(c)
save("02_zscore_dist")

# TODO(A): are children with missing z-scores different (state / wealth)? Add that check here.
df.to_csv(CLEAN, index=False)
print("saved", CLEAN)
