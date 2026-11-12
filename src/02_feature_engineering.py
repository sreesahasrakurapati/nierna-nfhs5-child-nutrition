"""PERSON C - feature engineering.  Input: nfhs5_clean.csv  ->  Output: nfhs5_features.csv"""
from common import *

df = pd.read_csv(CLEAN)
flag = lambda cond, base: np.where(base.isna(), np.nan, cond.astype(float))
df["stunted"]       = flag(df.haz < -2, df.haz)
df["severe_stunt"]  = flag(df.haz < -3, df.haz)
df["wasted"]        = flag(df.whz < -2, df.whz)
df["severe_wasted"] = flag(df.whz < -3, df.whz)
df["underweight"]   = flag(df.waz < -2, df.waz)
df["overweight"]    = flag(df.whz > 2, df.whz)
three = df[["stunted","wasted","underweight"]]
df["any_failure"] = np.where(three.isna().all(axis=1), np.nan, (three.fillna(0).sum(axis=1) > 0).astype(float))
df["n_failures"]  = three.sum(axis=1, min_count=1)
df["age_group"] = pd.cut(df.age_months, [-1,5,11,23,35,47,59],
                         labels=["0-5","6-11","12-23","24-35","36-47","48-59"])
df["low_birth_wt"] = flag(df.birth_weight_g < 2500, df.birth_weight_g)
df["bw_recorded"]  = df.birth_weight_g.notna().astype(int)
df["multiple_child_mother"] = (df.groupby("caseid").caseid.transform("size") > 1).astype(int)
df["birth_season"] = df.birth_month.map(lambda m: "Winter" if m in (11,12,1,2) else "Summer" if m in (3,4,5)
                                         else "Monsoon" if m in (6,7,8,9) else "Post-monsoon")
df["bmi_proxy"] = df.weight_kg / (df.height_cm/100)**2
df["wealth_rank"] = df.wealth_quintile.map({"Poorest":1,"Poorer":2,"Middle":3,"Richer":4,"Richest":5})
df["edu_rank"] = df.mother_edu.map({"No education":0,"Primary":1,"Secondary":2,"Higher":3})

print("National (weighted): stunting %.1f%% | wasting %.1f%% | underweight %.1f%% | any failure %.1f%%" %
      tuple(wmean(df, c) for c in ["stunted","wasted","underweight","any_failure"]))
df.to_csv(FEATURES, index=False)
print("saved", FEATURES)
