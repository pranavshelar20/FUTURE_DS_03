"""Step 1 - Clean & structure the raw UCI Bank Marketing data (bank-additional-full)."""
import pandas as pd, numpy as np

RAW = "data/raw/bank-additional-full.csv"
OUT = "data/processed/bank_marketing_clean.csv"

df = pd.read_csv(RAW, sep=";")
df.columns = [c.replace(".", "_") for c in df.columns]
n_raw = len(df)

# --- quality checks -------------------------------------------------------
assert df.isna().sum().sum() == 0                       # no true nulls
df = df.drop_duplicates().reset_index(drop=True)        # 12 exact duplicates
n_dup = n_raw - len(df)

# 'unknown' is a legitimate category in this dataset - keep it, flag it.
# --- feature engineering --------------------------------------------------
df["converted"] = (df["y"] == "yes").astype(int)
df["previously_contacted"] = (df["pdays"] != 999).astype(int)     # 999 = never contacted
df["pdays"] = df["pdays"].replace(999, np.nan)

df["age_band"] = pd.cut(df["age"], [0, 24, 34, 44, 54, 64, 120],
                        labels=["<25", "25-34", "35-44", "45-54", "55-64", "65+"])
df["attempt_band"] = pd.cut(df["campaign"], [0, 1, 2, 3, 4, 6, 100],
                            labels=["1", "2", "3", "4", "5-6", "7+"])

# Funnel stages (call-engagement proxy - see README):
#  S1 Contacted  : every record
#  S2 Engaged    : talked > 60s (got past the brush-off)
#  S3 Interested : talked > 180s (real conversation / pitch heard)
#  S4 Subscribed : y == yes
df["s1_contacted"] = 1
df["s2_engaged"] = (df["duration"] > 60).astype(int)
df["s3_interested"] = (df["duration"] > 180).astype(int)
df["s4_subscribed"] = df["converted"]

# Row order in the source is chronological (May-2008 -> Nov-2010).
# Infer calendar year by detecting month wrap-arounds.
mnum = df["month"].map({m: i + 1 for i, m in enumerate(
    ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"])})
year, prev = 2008, mnum.iloc[0]; yrs = []
for m in mnum:
    if m < prev - 3: year += 1                         # e.g. dec -> mar
    yrs.append(year); prev = m
df["year_inferred"] = yrs
df["month_num"] = mnum
df["period"] = df["year_inferred"].astype(str) + "-" + df["month_num"].astype(str).str.zfill(2)
df["quarter"] = df["year_inferred"].astype(str) + "-Q" + ((df["month_num"] - 1)//3 + 1).astype(str)

df.to_csv(OUT, index=False)
print(f"raw rows {n_raw:,} | duplicates removed {n_dup} | clean rows {len(df):,}")
print(df.groupby("year_inferred").size())
print(df.groupby("period").size().to_string())
