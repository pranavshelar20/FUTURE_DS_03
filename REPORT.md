# Marketing Funnel & Conversion Performance – Analysis Report

**Business question:** Where do prospects drop out of the funnel, which channels/segments bring high-quality leads, and how can conversion be improved?
**Data:** UCI Bank Marketing (`bank-additional-full`) – 41,188 outbound telemarketing contacts for a term-deposit product (Portugal, May 2008 – Nov 2010). 12 exact duplicates removed → **41,176 contacts**.

## 1. Funnel definition
The dataset has no website traffic or separate lead stage, so the funnel is built from **call engagement** (a documented proxy):

| Stage | Definition | Contacts | % of contacted | Step conversion | Step drop-off |
|---|---|---|---|---|---|
| 1. Contacted | Every record | 41,176 | 100% | – | – |
| 2. Engaged | Call > 60 s | 36,892 | 89.6% | 89.6% | 10.4% |
| 3. Interested | Call > 180 s | 20,480 | 49.7% | 55.5% | **44.5%** |
| 4. Subscribed | Accepted deposit (`y = yes`) | 4,639 | **11.3%** | 22.6% | **77.4%** |

**Overall contact → customer conversion: 11.27%.** The two biggest leaks are *Engaged → Interested* (16.4k people lost) and *Interested → Subscribed* (15.8k lost).

## 2. Key findings

**Channel.** Cellular converts at **14.7%** vs **5.2%** for landline (2.8x), needs ~16 calls per sale vs ~55, and generates 83% of all sales from 63.5% of contacts. The gap sits at the last step: 29% of interested cellular callers subscribe vs 11% on landline.

**Lead quality (previous campaign outcome).** Previous-success customers convert at **65.1%** (5.8x average) and 92% of those who show interest subscribe. They are only 3.3% of contacts but 19.3% of all sales. Never-contacted leads convert at 8.8%.

**Repeated calling has sharply diminishing returns.** Conversion falls from 13.0% on first contact to 6.1% at 5+ attempts. Contacts that received 5+ calls absorbed **38% of all call attempts but delivered 6.6% of sales**; 7+ attempts cost ~240 calls per sale.

**Segments.** Students (31.4%), retirees (25.2%), under-25s (24.0%) and 65+ (47.3%) convert at 2–4x average but are a small share of contacts. Blue-collar (6.9%) and services (8.1%) are the largest low-yield pools (22.5% and 9.6% of contacts).

**Time & macro context.** Weekday matters little (9.9–12.1%). Month shows large swings (May 6.4% vs Mar/Sep/Oct/Dec 44–51%), but this is confounded: 2008 was mass calling during high interest rates (4.8% conversion across 27.7k contacts), while 2009–10 was small and targeted (19.5% and 52.1%). Conversion is **~4x average when Euribor < 1%** and ~0.4x above 3%.

**Call duration.** Calls over 10 minutes convert at 48.6%; under 60 s convert at ~0%. Duration is only known *after* the call, so it is diagnostic (a sign the pitch landed) rather than a targeting variable.

## 3. Recommendations
1. **Make cellular the primary channel**; use landline only as a fallback.
2. **Cap attempts at 3–4 per lead** and redeploy the saved ~38% of call capacity to fresh/warm leads.
3. **Call previous-success customers first** (65% conversion) – build a retention / cross-sell list.
4. **Target high-propensity segments** (students, retirees, <25, 65+) with tailored offers; reduce spend on low-yield blue-collar/services cold lists or test new pitches there.
5. **Fix Engaged → Interested (44% drop):** A/B test opening scripts and a stronger value hook in the first 60 seconds.
6. **Fix Interested → Subscribed (77% drop):** add follow-up (SMS/email recap), a clear next step, and objection-handling training.
7. **Plan around the rate cycle:** push volume when rates are low; reposition the offer when rates are high.

## 4. Limitations
- Funnel stages are a proxy (call length), not true web → lead → customer stages.
- Year is inferred from the chronological row order; Month/Year/Euribor are confounded, so seasonal effects are not causal.
- Findings are associations from observational data; recommendations should be validated with A/B tests.
- Customer-level attempt counts reflect the campaign outcome (people who said yes stop being called), which exaggerates the "more calls = worse" pattern; the cap should be tested, not assumed.
