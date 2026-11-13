"""PERSON C - feature selection, PCA, district clustering.
Input:  nfhs5_features.csv
Output: figures 07, 08, 15, 16 | data/processed/district_profile.csv, cluster_profile.csv, choose_k_metrics.csv
"""
import itertools
from common import *
from sklearn.feature_selection import mutual_info_classif
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, silhouette_score, davies_bouldin_score, adjusted_rand_score
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

OUT = DISTRICT.parent
df = pd.read_csv(FEATURES)

# =====================================================================================
# 1. Feature selection for child stunting
#    haz/waz/whz/height/weight excluded on purpose: they define the target (leakage).
# =====================================================================================
feat = ["age_months","sex","residence","mother_edu","wealth_quintile","caste","state_code","birth_weight_g",
        "birth_order_idx","birth_season","bw_recorded","multiple_child_mother"]
d = df.dropna(subset=["stunted"]).copy()
d["state_code"] = d.state_code.astype(int).astype(str)          # a code, not a number -> one-hot
X = pd.get_dummies(d[feat], drop_first=True).astype(float)
X["birth_weight_g"] = X.birth_weight_g.fillna(X.birth_weight_g.median())
y = d.stunted.astype(int)
mi = pd.Series(mutual_info_classif(X, y, random_state=0), X.columns).sort_values(ascending=False)
print("Mutual information (top 10):\n", mi.head(10).round(4))
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.25, stratify=y, random_state=0)
rf = RandomForestClassifier(300, min_samples_leaf=20, n_jobs=-1, random_state=0).fit(Xtr, ytr)
print("RF AUC:", round(roc_auc_score(yte, rf.predict_proba(Xte)[:,1]), 3))
imp = pd.Series(rf.feature_importances_, X.columns).sort_values(ascending=False).head(12)
plt.figure(figsize=(7,4.5)); sns.barplot(x=imp.values, y=imp.index, color="#8172B2")
plt.title("Random-forest importance (stunting)"); save("07_importance")

# =====================================================================================
# 2. Child-level PCA on the four z-scores only.
#    Raw height/weight are left out: they mostly measure AGE (a 4-year-old is taller than
#    a baby), which would hijack a component. z-scores are already age- and sex-adjusted.
# =====================================================================================
zcols = ["haz","waz","whz","baz"]
block = df[zcols].dropna()
Zc = StandardScaler().fit_transform(block)
pca_c = PCA().fit(Zc); ev = pca_c.explained_variance_ratio_
print("\nChild PCA explained variance:", ev.round(3), "cumulative:", ev.cumsum().round(3))
print(pd.DataFrame(pca_c.components_[:2].T, index=zcols, columns=["PC1","PC2"]).round(2))
fig, ax = plt.subplots(1,2, figsize=(11,4))
ax[0].plot(range(1,len(ev)+1), ev.cumsum(), "o-"); ax[0].set_title("Child PCA: cumulative variance")
ax[0].set_xlabel("components"); ax[0].set_ylim(0, 1.05)
sc = pca_c.transform(Zc)[:5000]; ax[1].scatter(sc[:,0], sc[:,1], s=3, alpha=.4)
ax[1].set_title("PC1 vs PC2 (5k sample)"); ax[1].set_xlabel("PC1"); ax[1].set_ylabel("PC2")
save("08_pca")

# =====================================================================================
# 3. District profiles (all shares survey-weighted, team rule 1)
# =====================================================================================
SHARES = {"stunting":"stunted", "wasting":"wasted", "underweight":"underweight", "low_bw":"low_birth_wt",
          "pct_poorest":"is_poorest", "pct_mom_no_edu":"mom_no_edu", "pct_rural":"is_rural",
          "pct_implausible":"implausible_any", "pct_haz_missing":"haz_missing"}
dist = df.groupby(["state","district_code"]).apply(
    lambda g: pd.Series({"n": len(g), **{k: wmean(g, v) for k, v in SHARES.items()}}),
    include_groups=False).reset_index()
small = dist[dist.n < 30]
print(f"\nDistricts: {len(dist)} | dropped (n < 30): {len(small)}")
dist = dist[dist.n >= 30].reset_index(drop=True)

# Cluster on burden + drivers. Data-quality columns are NOT clustered on;
# they are reported per cluster afterwards so we can see if a group also has poor data.
cols = ["stunting","wasting","underweight","low_bw","pct_poorest","pct_mom_no_edu","pct_rural"]
Xd = StandardScaler().fit_transform(dist[cols].fillna(dist[cols].mean()))

# ---- district-level PCA, keep PCs explaining >= 80% ----
pca_d = PCA().fit(Xd)
n_pc = int(np.searchsorted(pca_d.explained_variance_ratio_.cumsum(), 0.80) + 1)
Zd = pca_d.transform(Xd)[:, :n_pc]
print(f"District PCA: keep {n_pc} PCs ({pca_d.explained_variance_ratio_[:n_pc].sum():.1%} of variance)")
print(pd.DataFrame(pca_d.components_[:n_pc].T, index=cols,
                   columns=[f"PC{i+1}" for i in range(n_pc)]).round(2))

# =====================================================================================
# 4. Choosing k: elbow + silhouette + Davies-Bouldin + stability across seeds
# =====================================================================================
rows = []
for k in range(2, 11):
    fits = [KMeans(k, n_init=20, random_state=s).fit(Zd) for s in range(10)]
    best = min(fits, key=lambda f: f.inertia_)
    rows.append({"k": k, "inertia": best.inertia_,
                 "silhouette": silhouette_score(Zd, best.labels_),
                 "davies_bouldin": davies_bouldin_score(Zd, best.labels_),
                 "stability_ari": np.mean([adjusted_rand_score(a.labels_, b.labels_)
                                           for a, b in itertools.combinations(fits, 2)]),
                 "smallest_cluster": np.bincount(best.labels_).min()})
km = pd.DataFrame(rows); km.to_csv(OUT / "choose_k_metrics.csv", index=False)
print("\nChoosing k:\n", km.round(3).to_string(index=False))
print("Best silhouette at k =", int(km.loc[km.silhouette.idxmax(), "k"]))

K = 4   # <- set this after reading the table above; justify it in notes/C_features_notes.md
fig, ax = plt.subplots(1, 3, figsize=(14, 4))
for a, col, t in [(ax[0],"inertia","Elbow (inertia, lower = tighter)"),
                  (ax[1],"silhouette","Silhouette (higher = better)"),
                  (ax[2],"stability_ari","Stability across 10 seeds (ARI)")]:
    a.plot(km.k, km[col], "o-"); a.axvline(K, ls="--", c="grey"); a.set_title(t); a.set_xlabel("k")
save("15_choose_k")

# =====================================================================================
# 5. Final clusters, numbered 1 = lowest stunting ... K = highest
# =====================================================================================
lab = KMeans(K, n_init=20, random_state=0).fit_predict(Zd)
order = dist.groupby(lab).stunting.mean().sort_values().index
dist["cluster"] = pd.Series(lab).map({c: i+1 for i, c in enumerate(order)})
for i in range(n_pc): dist[f"PC{i+1}"] = Zd[:, i]

prof = dist.groupby("cluster").agg(districts=("n","size"), children=("n","sum"),
                                   **{c: (c,"mean") for c in cols + ["pct_implausible","pct_haz_missing"]})
print("\nCluster profiles (mean of district %):\n", prof.round(1).to_string())
for c in prof.index:
    top = dist[dist.cluster == c].nlargest(3, "stunting")
    print(f"  cluster {c} e.g.: " + ", ".join(f"{s} #{int(x)}" for s, x in zip(top.state, top.district_code)))
print("Spearman stunting vs mother-no-edu (district):", round(dist.stunting.corr(dist.pct_mom_no_edu, method="spearman"),2))
print("Spearman stunting vs implausible % (district):", round(dist.stunting.corr(dist.pct_implausible, method="spearman"),2))

fig, ax = plt.subplots(figsize=(7.5,5))
s = ax.scatter(dist.PC1, dist.PC2 if n_pc > 1 else np.zeros(len(dist)), c=dist.cluster, cmap="viridis", s=14)
ax.legend(*s.legend_elements(), title="Cluster", frameon=False)
ax.set_xlabel("PC1"); ax.set_ylabel("PC2"); ax.set_title(f"{len(dist)} districts in PCA space, k={K}")
save("16_district_clusters")

dist.to_csv(DISTRICT, index=False)
prof.round(2).to_csv(OUT / "cluster_profile.csv")
print("saved", DISTRICT, "and cluster_profile.csv")
