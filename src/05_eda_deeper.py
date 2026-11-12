"""PERSON B - deeper EDA (stretch tasks). Input: nfhs5_features.csv -> charts 09-11 in reports/figures"""
from common import *

df = pd.read_csv(FEATURES)
W = ["Poorest", "Poorer", "Middle", "Richer", "Richest"]
E = ["No education", "Primary", "Secondary", "Higher"]
AG = ["0-5", "6-11", "12-23", "24-35", "36-47", "48-59"]

# ---- Task 1: wealth inside each education level -------------------------------------
# Question: does wealth still matter when mother's education is the same? And the reverse?
tab = df.groupby(["mother_edu", "wealth_quintile"]).apply(
    lambda g: pd.Series({"stunting_pct": wmean(g, "stunted"), "n": g.stunted.notna().sum()}),
    include_groups=False).reset_index()
heat = tab.pivot(index="mother_edu", columns="wealth_quintile", values="stunting_pct").reindex(index=E, columns=W)
counts = tab.pivot(index="mother_edu", columns="wealth_quintile", values="n").reindex(index=E, columns=W)
print("Weighted stunting % (rows = mother's education, columns = wealth):\n", heat.round(1).to_string())
print("\nNumber of children in each cell (small cells = less reliable):\n", counts.astype(int).to_string())
plt.figure(figsize=(7, 4)); sns.heatmap(heat, annot=True, fmt=".1f", cmap="Reds", cbar_kws={"label": "stunting %"})
plt.title("Stunting % by mother's education and wealth"); plt.xlabel("Wealth quintile"); plt.ylabel("Mother's education")
save("09_wealth_by_education")

# ---- Task 2: urban / rural gap after accounting for wealth ---------------------------
ur = df.groupby(["wealth_quintile", "residence"]).apply(lambda g: wmean(g, "stunted"), include_groups=False).unstack().reindex(W)
print("\nStunting % by wealth and residence:\n", ur.round(1).to_string())
print("Rural minus urban gap within each wealth group:\n", (ur.Rural - ur.Urban).round(1).to_string())

# ---- Task 3: sex gap (overall and by age group) --------------------------------------
sex = df.groupby(["age_group", "sex"]).apply(lambda g: wmean(g, "stunted"), include_groups=False).unstack().reindex(AG)
print("\nStunting % by age group and sex:\n", sex.round(1).to_string())
print("Overall:", prev(df, "sex").round(1).to_dict())
sex.plot(kind="bar", figsize=(7, 4)); plt.ylabel("stunting %"); plt.title("Stunting by age group and sex")
plt.xticks(rotation=0); save("10_sex_gap")

# ---- Task 4: birth season -------------------------------------------------------------
seas = prev(df, "birth_season").reindex(["Winter", "Summer", "Monsoon", "Post-monsoon"])
print("\nStunting % by birth season:\n", seas.round(1).to_string())

# ---- Task 5: age x wealth (how the gap opens with age) -------------------------------
aw = df.groupby(["age_group", "wealth_quintile"], observed=True).apply(lambda g: wmean(g, "stunted"), include_groups=False).unstack().reindex(AG)[W]
print("\nStunting % by age group and wealth:\n", aw.round(1).to_string())
aw[["Poorest", "Middle", "Richest"]].plot(marker="o", figsize=(7, 4)); plt.ylabel("stunting %")
plt.title("The wealth gap opens with age"); save("11_age_by_wealth")
