"""PERSON C - feature selection, PCA, district clustering.  Input: nfhs5_features.csv"""
from common import *
from sklearn.feature_selection import mutual_info_classif
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

df = pd.read_csv(FEATURES)

# ---- feature selection (haz/waz/height excluded on purpose: they define the target = leakage) ----
feat = ["age_months","sex","residence","mother_edu","wealth_quintile","caste","state_code","birth_weight_g",
        "birth_order_idx","birth_season","bw_recorded","multiple_child_mother"]
d = df.dropna(subset=["stunted"]).copy()
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

# ---- PCA on the anthropometric block ----
block = df[["haz","waz","whz","baz","weight_kg","height_cm"]].dropna()
Z = StandardScaler().fit_transform(block)
pca = PCA().fit(Z); ev = pca.explained_variance_ratio_
print("Explained variance:", ev.round(3), "cumulative:", ev.cumsum().round(3))
print(pd.DataFrame(pca.components_[:2].T, index=block.columns, columns=["PC1","PC2"]).round(2))
fig, ax = plt.subplots(1,2, figsize=(11,4))
ax[0].plot(range(1,len(ev)+1), ev.cumsum(), "o-"); ax[0].set_title("PCA cumulative variance"); ax[0].set_xlabel("components")
sc = pca.transform(Z)[:5000]; ax[1].scatter(sc[:,0], sc[:,1], s=3, alpha=.4); ax[1].set_title("PC1 vs PC2 (5k sample)")
save("08_pca")

# ---- district profiles + clusters ----
dist = df.groupby(["state","district_code"]).apply(lambda g: pd.Series({
    "n": len(g), "stunting": wmean(g,"stunted"), "wasting": wmean(g,"wasted"), "underweight": wmean(g,"underweight"),
    "pct_poorest": (g.wealth_quintile=="Poorest").mean()*100, "pct_mom_no_edu": (g.mother_edu=="No education").mean()*100,
    "pct_rural": (g.residence=="Rural").mean()*100}), include_groups=False).reset_index()
dist = dist[dist.n >= 30]
cols = ["stunting","wasting","underweight","pct_poorest","pct_mom_no_edu","pct_rural"]
dist["cluster"] = KMeans(4, n_init=10, random_state=0).fit_predict(StandardScaler().fit_transform(dist[cols].fillna(dist[cols].mean())))
print(dist.groupby("cluster")[cols+["n"]].mean().round(1).to_string())
print("Spearman stunting vs mother-no-edu (district):", round(dist.stunting.corr(dist.pct_mom_no_edu, method="spearman"),2))
dist.to_csv(DISTRICT, index=False)
# TODO(C): justify k=4 (elbow / silhouette) before presenting
