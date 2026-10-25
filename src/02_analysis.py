"""Step 2 - Funnel metrics, segment comparisons, tables + charts + dashboard JSON."""
import pandas as pd, numpy as np, json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("data/processed/bank_marketing_clean.csv")
T = "outputs/tables/"; C = "outputs/charts/"
N = len(df); CONV = df.converted.sum()
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titleweight": "bold", "figure.dpi": 130})
BLUE, ORANGE, GREY, RED, GREEN = "#2563eb", "#f59e0b", "#94a3b8", "#dc2626", "#16a34a"

def rate(s): return round(100 * s.mean(), 2)
def seg(col, order=None, min_n=0):
    g = df.groupby(col, observed=True).agg(contacts=("converted", "size"), conversions=("converted", "sum"),
            avg_attempts=("campaign", "mean"), total_calls=("campaign", "sum"),
            avg_duration=("duration", "mean"))
    g["conv_rate_pct"] = (100 * g.conversions / g.contacts).round(2)
    g["calls_per_conversion"] = (g.total_calls / g.conversions).round(1)
    g["share_of_contacts_pct"] = (100 * g.contacts / N).round(1)
    g["share_of_conversions_pct"] = (100 * g.conversions / CONV).round(1)
    g["lift_vs_avg"] = (g.conv_rate_pct / (100 * CONV / N)).round(2)
    g = g.round(1).reset_index()
    g = g[g.contacts >= min_n]
    if order: g = g.set_index(col).loc[[o for o in order if o in set(g[col])]].reset_index()
    else: g = g.sort_values("conv_rate_pct", ascending=False)
    return g

# ---------------- 1. FUNNEL ------------------------------------------------
stages = [("Contacted", "s1_contacted"), ("Engaged (>60s)", "s2_engaged"),
          ("Interested (>180s)", "s3_interested"), ("Subscribed", "s4_subscribed")]
rows = []; prev = N
for name, col in stages:
    n = int(df[col].sum())
    rows.append(dict(stage=name, users=n, pct_of_contacted=round(100*n/N, 2),
                     step_conversion_pct=round(100*n/prev, 2), step_dropoff_pct=round(100*(1-n/prev), 2),
                     users_lost=prev-n)); prev = n
funnel = pd.DataFrame(rows); funnel.to_csv(T+"funnel_overall.csv", index=False)
print(funnel.to_string())

# funnel by channel / by period / by prior outcome
def funnel_by(col):
    out = []
    for k, g in df.groupby(col, observed=True):
        out.append(dict(**{col: k}, contacted=len(g), engaged_pct=rate(g.s2_engaged),
            interested_pct=rate(g.s3_interested), subscribed_pct=rate(g.s4_subscribed),
            engaged_to_interested_pct=round(100*g.s3_interested.sum()/max(g.s2_engaged.sum(),1),1),
            interested_to_sub_pct=round(100*g.s4_subscribed.sum()/max(g.s3_interested.sum(),1),1)))
    return pd.DataFrame(out)
fch = funnel_by("contact"); fch.to_csv(T+"funnel_by_channel.csv", index=False)
fpo = funnel_by("poutcome"); fpo.to_csv(T+"funnel_by_prior_outcome.csv", index=False)

# ---------------- 2. SEGMENTS ----------------------------------------------
months = ["mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
dow = ["mon","tue","wed","thu","fri"]
tabs = {
 "channel": seg("contact"),
 "month": seg("month", months),
 "weekday": seg("day_of_week", dow),
 "job": seg("job"),
 "age_band": seg("age_band", ["<25","25-34","35-44","45-54","55-64","65+"]),
 "education": seg("education", min_n=100),
 "prior_outcome": seg("poutcome"),
 "attempts": seg("attempt_band", ["1","2","3","4","5-6","7+"]),
 "quarter": seg("quarter", sorted(df.quarter.unique())),
 "year": seg("year_inferred"),
}
df["duration_band"] = pd.cut(df.duration, [-1,60,120,180,300,600,10000],
        labels=["0-60s","60-120s","2-3m","3-5m","5-10m","10m+"])
tabs["duration"] = seg("duration_band", ["0-60s","60-120s","2-3m","3-5m","5-10m","10m+"])
df["euribor_band"] = pd.cut(df.euribor3m, [0,1,3,4.5,6], labels=["<1% (low rates)","1-3%","3-4.5%","4.5%+ (high)"])
tabs["euribor"] = seg("euribor_band", ["<1% (low rates)","1-3%","3-4.5%","4.5%+ (high)"])
for k, v in tabs.items(): v.to_csv(T+f"segment_{k}.csv", index=False)

# diminishing returns of repeated calling
att = tabs["attempts"]
late = df[df.campaign >= 5]
waste = dict(calls_share_att5plus=round(100*late.campaign.sum()/df.campaign.sum(),1),
             contacts_att5plus=len(late), conv_att5plus=int(late.converted.sum()),
             conv_share_att5plus=round(100*late.converted.sum()/CONV,1),
             rate_att5plus=rate(late.converted), rate_att1=rate(df[df.campaign==1].converted))
print("WASTE", waste)

# best-vs-worst combined segment
df["seg"] = df.contact + " | " + df.poutcome
combo = seg("seg", min_n=300); combo.to_csv(T+"segment_channel_x_prior.csv", index=False)
print(combo[["seg","contacts","conv_rate_pct","lift_vs_avg"]].to_string())

# high-intent segments (>=300 contacts) across age/job/month
hi = df[(df.age>=60)|(df.job.isin(["student","retired"]))]
print("students/retired/60+ :", len(hi), rate(hi.converted))

# ---------------- 3. CHARTS --------------------------------------------------
# 3.1 funnel
fig, ax = plt.subplots(figsize=(9, 4.6))
cols = [BLUE, "#3b82f6", "#60a5fa", GREEN]
for i, r in funnel.iterrows():
    ax.barh(3-i, r.users, color=cols[i], height=.7)
    ax.text(r.users + N*.01, 3-i, f"{r.users:,}  ({r.pct_of_contacted:.1f}%)", va="center", fontweight="bold")
    if i: ax.text(N*.5, 3-i+.5, f"▼ {r.step_dropoff_pct:.0f}% drop", ha="center", color=RED, fontsize=9)
ax.set_yticks(range(4)); ax.set_yticklabels(funnel.stage[::-1]); ax.set_xlim(0, N*1.3)
ax.set_xticks([]); ax.spines["bottom"].set_visible(False)
ax.set_title("Overall funnel: Contacted → Subscribed (n = 41,176)"); plt.tight_layout()
plt.savefig(C+"01_funnel_overall.png"); plt.close()

# helper for bar charts
def bar(tab, col, fname, title, rot=0, hi_color=BLUE, figsize=(9,4.4), avg=True):
    fig, ax = plt.subplots(figsize=figsize)
    x = tab[col].astype(str); y = tab.conv_rate_pct
    b = ax.bar(x, y, color=[hi_color if v >= 100*CONV/N else GREY for v in y])
    for r, v, n in zip(b, y, tab.contacts):
        ax.text(r.get_x()+r.get_width()/2, v+.4, f"{v:.1f}%", ha="center", fontsize=9, fontweight="bold")
        ax.text(r.get_x()+r.get_width()/2, 0.4, f"n={n:,.0f}", ha="center", fontsize=7, color="white", rotation=90, va="bottom")
    if avg: ax.axhline(100*CONV/N, color=RED, ls="--", lw=1); ax.text(len(x)-.5, 100*CONV/N+.5, f"avg {100*CONV/N:.1f}%", color=RED, ha="right", fontsize=9)
    ax.set_ylabel("Conversion rate (%)"); ax.set_title(title); plt.xticks(rotation=rot, ha="right" if rot else "center")
    plt.tight_layout(); plt.savefig(C+fname); plt.close()

bar(tabs["channel"], "contact", "02_channel.png", "Conversion rate by contact channel", figsize=(6,4.4))
bar(tabs["month"], "month", "03_month.png", "Conversion rate by month (low-volume months are very high-converting)")
bar(tabs["weekday"], "day_of_week", "04_weekday.png", "Conversion rate by weekday", figsize=(6.5,4.4))
bar(tabs["job"], "job", "05_job.png", "Conversion rate by job segment", rot=35, figsize=(9.5,4.8))
bar(tabs["age_band"], "age_band", "06_age.png", "Conversion rate by age band", figsize=(6.5,4.4))
bar(tabs["prior_outcome"].sort_values("conv_rate_pct"), "poutcome", "07_prior_outcome.png", "Conversion by outcome of previous campaign", figsize=(6.5,4.4))
bar(tabs["attempts"], "attempt_band", "08_attempts.png", "Conversion falls with every extra call attempt", figsize=(7,4.4))
bar(tabs["duration"], "duration_band", "09_duration.png", "Conversion rate by call duration", figsize=(7.5,4.4))
bar(tabs["euribor"], "euribor_band", "10_euribor.png", "Conversion rate by Euribor 3-month rate", figsize=(7.5,4.4))

# 3.2 quarter trend
q = tabs["quarter"]
fig, ax = plt.subplots(figsize=(10, 4.4)); ax2 = ax.twinx()
ax.bar(q.quarter, q.contacts, color="#cbd5e1"); ax2.plot(q.quarter, q.conv_rate_pct, color=BLUE, marker="o", lw=2)
ax.set_ylabel("Contacts"); ax2.set_ylabel("Conversion rate (%)", color=BLUE); ax2.spines["right"].set_visible(True)
ax.set_title("Quarterly volume vs conversion (volume ↓, quality ↑ after 2008)"); plt.xticks(rotation=45)
plt.tight_layout(); plt.savefig(C+"11_quarterly_trend.png"); plt.close()

# 3.3 share of calls vs share of conversions by attempt
fig, ax = plt.subplots(figsize=(7.5, 4.4)); w = .38; xs = np.arange(len(att))
ax.bar(xs-w/2, att.share_of_contacts_pct, w, label="% of contacts", color=GREY)
ax.bar(xs+w/2, att.share_of_conversions_pct, w, label="% of conversions", color=GREEN)
ax.set_xticks(xs); ax.set_xticklabels(att.attempt_band); ax.set_xlabel("Number of contacts in campaign")
ax.legend(frameon=False); ax.set_title("Heavy calling over-consumes effort relative to results")
plt.tight_layout(); plt.savefig(C+"12_attempts_share.png"); plt.close()

# ---------------- 4. DASHBOARD JSON ------------------------------------------
def recs(t, cols): return t[cols].to_dict("records")
base = ["contacts","conversions","conv_rate_pct","lift_vs_avg","calls_per_conversion","share_of_contacts_pct","share_of_conversions_pct"]
payload = dict(
  kpi=dict(contacts=int(N), conversions=int(CONV), conv_rate=round(100*CONV/N,2),
           engaged_rate=funnel.pct_of_contacted[1], interested_rate=funnel.pct_of_contacted[2],
           avg_calls_per_contact=round(df.campaign.mean(),2), calls_per_conv=round(df.campaign.sum()/CONV,1)),
  funnel=funnel.to_dict("records"),
  funnel_channel=fch.to_dict("records"), funnel_prior=fpo.to_dict("records"),
  waste=waste,
  seg={k: recs(v, [v.columns[0]]+base) for k, v in tabs.items()},
  combo=recs(combo.head(8), ["seg"]+base),
)
json.dump(payload, open("dashboard/data.json","w"), indent=1, default=float)
print("done")
