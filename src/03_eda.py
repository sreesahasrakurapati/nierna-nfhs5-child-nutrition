"""PERSON B - exploratory analysis.  Input: nfhs5_features.csv  ->  figures in reports/figures"""
from common import *

df = pd.read_csv(FEATURES)
df["age_group"] = pd.Categorical(df.age_group, ["0-5","6-11","12-23","24-35","36-47","48-59"], ordered=True)

# 1. age pattern
age = df.groupby("age_months")[["haz","waz","whz"]].mean()
age.plot(figsize=(8,4)); plt.axhline(-2, color="r", ls="--"); plt.title("Mean z-score by age (months)"); save("03_age_curve")
print("Stunting by age group:\n", prev(df, "age_group").round(1))
# 2. state ranking
st = prev(df, "state").sort_values(); plt.figure(figsize=(7,9)); sns.barplot(x=st.values, y=st.index, color="#C44E52")
plt.xlabel("Weighted stunting %"); plt.title("Stunting by state/UT"); save("04_state_stunting")
# 3. socio-economic gradients
fig, ax = plt.subplots(1,4, figsize=(16,3.8))
for a, (by, order) in zip(ax, [("wealth_quintile",["Poorest","Poorer","Middle","Richer","Richest"]),
        ("mother_edu",["No education","Primary","Secondary","Higher"]), ("residence",["Rural","Urban"]),
        ("caste",["ST","SC","OBC","General/None","Not recorded"])]):
    p = prev(df, by).reindex(order); sns.barplot(x=p.index, y=p.values, ax=a, color="#55A868")
    a.set_title(f"Stunting % by {by}"); a.tick_params(axis="x", rotation=30)
save("05_socio_gradients")
# 4. birth weight
tmp = df.dropna(subset=["low_birth_wt"])
print("Stunting by low-birth-weight:", prev(tmp, "low_birth_wt").round(1).to_dict())
print("Stunting by birth-weight recorded:", prev(df, "bw_recorded").round(1).to_dict())
# 5. correlations
num = ["haz","waz","whz","baz","age_months","weight_kg","height_cm","birth_weight_g","wealth_rank","edu_rank","birth_order_idx"]
plt.figure(figsize=(8,6.5)); sns.heatmap(df[num].corr(), annot=True, fmt=".2f", cmap="coolwarm", center=0)
plt.title("Correlation (Pearson)"); save("06_corr")
# 6. outliers within age month (kept, not deleted: they are real short/thin children)
def iqr_flag(g, c):
    q1, q3 = g[c].quantile([.25,.75]); i = q3-q1
    return (g[c] < q1-1.5*i) | (g[c] > q3+1.5*i)
out = df.groupby("age_months", group_keys=False).apply(lambda g: iqr_flag(g,"height_cm"), include_groups=False)
print("height outliers within age:", int(out.sum()))
# TODO(B): write pattern / reason / action for each chart in notes/B_eda_notes.md
