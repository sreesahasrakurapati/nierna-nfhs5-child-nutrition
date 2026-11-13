"""PERSON C - feature engineering.  Input: nfhs5_clean.csv  ->  Output: nfhs5_features.csv"""
from common import *

df = pd.read_csv(CLEAN)
flag = lambda cond, base: np.where(base.isna(), np.nan, cond.astype(float))

# ---- outcome flags (WHO cut-offs) ----
df["stunted"]       = flag(df.haz < -2, df.haz)
df["severe_stunt"]  = flag(df.haz < -3, df.haz)
df["wasted"]        = flag(df.whz < -2, df.whz)
df["severe_wasted"] = flag(df.whz < -3, df.whz)
df["underweight"]   = flag(df.waz < -2, df.waz)
df["overweight"]    = flag(df.whz > 2, df.whz)
three = df[["stunted","wasted","underweight"]]
df["any_failure"] = np.where(three.isna().all(axis=1), np.nan, (three.fillna(0).sum(axis=1) > 0).astype(float))
df["n_failures"]  = three.sum(axis=1, min_count=1)

# ---- child / birth features ----
df["age_group"] = pd.cut(df.age_months, [-1,5,11,23,35,47,59],
                         labels=["0-5","6-11","12-23","24-35","36-47","48-59"])
df["low_birth_wt"] = flag(df.birth_weight_g < 2500, df.birth_weight_g)
df["bw_recorded"]  = df.birth_weight_g.notna().astype(int)
df["multiple_child_mother"] = (df.groupby("caseid").caseid.transform("size") > 1).astype(int)
SEASON = {11:"Winter",12:"Winter",1:"Winter",2:"Winter",3:"Summer",4:"Summer",5:"Summer",
          6:"Monsoon",7:"Monsoon",8:"Monsoon",9:"Monsoon",10:"Post-monsoon"}
df["birth_season"] = df.birth_month.map(SEASON)          # missing month stays missing

# BMI only for children whose measurements passed the WHO screen (baz kept),
# otherwise a 20 cm / 77 kg entry error would give an absurd BMI.
df["bmi_proxy"] = np.where(df.baz.notna(), df.weight_kg / (df.height_cm/100)**2, np.nan)

# ---- socio-economic ranks + indicators (used for weighted district shares) ----
df["wealth_rank"] = df.wealth_quintile.map({"Poorest":1,"Poorer":2,"Middle":3,"Richer":4,"Richest":5})
df["edu_rank"] = df.mother_edu.map({"No education":0,"Primary":1,"Secondary":2,"Higher":3})
df["is_poorest"]  = (df.wealth_quintile == "Poorest").astype(float)
df["mom_no_edu"]  = (df.mother_edu == "No education").astype(float)
df["is_rural"]    = (df.residence == "Rural").astype(float)

# ---- data-quality features (link to our problem statement: entry errors vs real risk) ----
# DHS already flags implausible measurements with codes in the raw file:
#   9996 = height/weight out of plausible limits, 9997 = age out of limits, 9998 = z-score flagged (WHO range)
#   9999 = simply missing (NOT an error).
# Cleaning turns all of them into NaN, so we read the codes back from the raw file to tell them apart.
ZRAW = {"hw70": "haz", "hw71": "waz", "hw72": "whz", "hw73": "baz"}
raw = pd.read_csv(RAW, usecols=["caseid", "midx", *ZRAW])
for r, z in ZRAW.items():
    raw[f"dhs_flag_{z}"] = raw[r].isin([9996, 9997, 9998]).astype(float)
raw = raw.drop(columns=list(ZRAW)).rename(columns={"midx": "birth_order_idx"})
key = ["caseid", "birth_order_idx"]
if not raw.duplicated(key).any() and not df.duplicated(key).any():
    df = df.merge(raw, on=key, how="left", validate="one_to_one")
else:                                   # fall back to row order (cleaning keeps every row)
    assert len(raw) == len(df), "row counts differ - cannot align raw flags"
    for z in ZRAW.values(): df[f"dhs_flag_{z}"] = raw[f"dhs_flag_{z}"].values

flags = [f"dhs_flag_{z}" for z in ["haz", "waz", "whz"]] + [c for c in ["bad_haz","bad_waz","bad_whz"] if c in df]
df["implausible_any"] = df[flags].fillna(0).astype(bool).any(axis=1).astype(float)  # flagged as measurement/entry error
df["haz_missing"]     = df.haz.isna().astype(float)                                   # no usable height-for-age

print("National (weighted): stunting %.1f%% | wasting %.1f%% | underweight %.1f%% | any failure %.1f%%" %
      tuple(wmean(df, c) for c in ["stunted","wasted","underweight","any_failure"]))
print("Implausible (DHS-flagged HAZ/WAZ/WHZ): %.2f%% | HAZ missing: %.1f%%" %
      (wmean(df, "implausible_any"), wmean(df, "haz_missing")))
df.to_csv(FEATURES, index=False)
print("saved", FEATURES)
