# Table Pattern Examples

Concrete examples of well-executed table patterns from production documentation. Use these as templates when building tables in technical documents.

## Contents

1. [Summary Matrices](#summary-matrices)
2. [Metrics Tables](#metrics-tables)
3. [Trend Tables](#trend-tables)
4. [Gap Analysis Tables](#gap-analysis-tables)
5. [Comparison Tables with Deltas](#comparison-tables-with-deltas)
6. [Changes Applied Tables](#changes-applied-tables)
7. [Cost Scalability Tables](#cost-scalability-tables)
8. [Roadmap Tables](#roadmap-tables)
9. [Troubleshooting Tables](#troubleshooting-tables)
10. [Quick Reference Tables](#quick-reference-tables)
11. [File Reference Tables](#file-reference-tables)

---

## Summary Matrices

The most important table in a feasibility study. Gives the reader the full picture at a glance: feasibility rating, effort, and the specific blocker for each area.

```markdown
| Area                           | Feasibility | Estimated Effort | Key Blocker                                                       |
| ------------------------------ | ----------- | ---------------- | ----------------------------------------------------------------- |
| **Option Processing**          | High        | 2–3 days         | `_process_proposals` always calls `process_pricing`               |
| **Current/Renewal Processing** | Medium-Low  | 5–8 days         | Pricing architecturally coupled to the core output structure      |
| **Database Schema**            | High        | 0 days           | Already fully supports nullable pricing                           |
| **Backend API Validation**     | High        | 0.5–1 day        | Enqueue guard in `run_routes.py` skips carriers without pricing   |
| **Frontend (Legacy)**          | Medium      | 1–2 days         | `hasInvalidCarrierDocsForProduct` blocks submission               |
| **Frontend (New/V2)**          | High        | < 0.5 day        | Minimal restrictions on pricing docs                              |
```

**Why this works:** Feasibility ratings use consistent HIGH/MEDIUM/LOW. Effort is concrete (days, not t-shirt sizes). Blockers reference specific code. "0 days" for database makes it clear no work is needed.

Follow a summary matrix with a total effort table:

```markdown
### Total Estimated Effort

| Scope                                                | Estimated Time |
| ---------------------------------------------------- | -------------- |
| **Option processing only** (recommended first phase) | **4–6 days**   |
| **Option + Current/Renewal processing** (full scope) | **9–14 days**  |
```

---

## Metrics Tables

For current state / performance snapshots. Keep columns to metric + value.

```markdown
| Metric                                            | Value                          |
| ------------------------------------------------- | ------------------------------ |
| Production runs completed                         | 41                             |
| Total AI cost (30 days)                           | $86.63                         |
| AI cost per case                                  | $2.11                          |
| Total infrastructure cost per case                | $6.86                          |
| Fields accepted by reviewers without modification | 76.5%                          |
| Fields with zero corrections (perfect extraction) | 6 field types at 100% accuracy |
```

---

## Trend Tables

For showing progression over time. Bold the current / latest column. Include a delta row.

```markdown
| Metric       | R1    | R2    | R3    | R4    | R5    | R6     | R7     | R8     | R9     | R10 (Current) |
|---|---|---|---|---|---|---|---|---|---|---|
| **Accuracy** | 58.3% | 68.0% | 69.9% | 70.9% | 71.8% | 77.95% | 72.87% | 77.35% | 79.41% | **81.14%**    |
| **Fields**   | 677   | 789   | 812   | 823   | 834   | 905    | 846    | 898    | 922    | **942**       |
| **Passed**   | 0     | 5     | 4     | 3     | 8     | 6      | 3      | 8      | 6      | **9**         |
| **Delta**    | —     | +112  | +23   | +11   | +11   | +71    | -59    | +52    | +24    | **+20**       |
```

**Note:** The delta row shows acceleration/deceleration at a glance.

---

## Gap Analysis Tables

For showing the path from current state to a target. Use running totals. Order by priority.

```markdown
- **Current:** 942 fields (81.14%)
- **85% Target:** 987 fields
- **Gap:** 45 fields

| Priority | Action                                          | Type              | Est. Fields | Running Total | Accuracy |
|---|---|---|---|---|---|
| 1        | Cigna copay format `$X copay` → `$X copay/visit`| Golden data       | ~9          | 951           | 81.9%    |
| 2        | Aetna 723 "coinsurance" → "after ded"           | Golden data       | ~8          | 959           | 82.6%    |
| 3        | BSC location labels "Lab:" → "Radiology Center:" | Golden data      | ~8          | 967           | 83.3%    |
| 4        | Cigna 655 chiro/acup golden format              | Golden data       | ~4          | 971           | 83.6%    |
| 5        | BSC copay format `$X/visit` → `$X copay/visit`  | Golden data       | ~6          | 977           | 84.1%    |
| 6        | Fix BSC 714 multi-location collapse             | Field description | ~6          | 983           | 84.7%    |
| 7        | Anthem pricing extraction                       | Field description | ~10         | 993           | 85.5%    |

**Priorities 1-5 (all golden data) would reach ~84%.** Adding the BSC multi-location fix and Anthem pricing improvements would approach 85.5%.
```

**Why this works:** "Running Total" and "Accuracy" columns show cumulative impact. "Type" distinguishes easy wins from harder work. Summary sentence identifies the natural break point.

---

## Comparison Tables with Deltas

When comparing two states, include both absolute values and deltas. Bold improvements and regressions.

```markdown
| Carrier              | Tests | Run 9       | Run 10          | Δ Fields | Δ Accuracy  | Passed  |
|---|---|---|---|---|---|---|
| **Anthem**           | 7     | 76.1% (229) | **83.1% (250)** | **+21**  | **+7.0pp**  | **3/7** |
| **UnitedHealthcare** | 3     | 81.4% (105) | **86.0% (111)** | **+6**   | **+4.7pp**  | **2/3** |
| **Cigna**            | 7     | 81.7% (246) | **82.4% (248)** | +2       | +0.6pp      | 2/7     |
| **Kaiser**           | 1     | 88.4% (38)  | **88.4% (38)**  | 0        | 0pp         | 1/1     |
| **Aetna**            | 3     | 82.2% (106) | **78.3% (101)** | **-5**   | **-3.9pp**  | 1/3     |
| **Blue Shield of CA**| 6     | 76.7% (198) | **75.2% (194)** | -4       | -1.5pp      | 0/6     |
```

**Note:** Include both percentage and absolute count — `83.1% (250)` — so the reader sees rate and scale.

---

## Changes Applied Tables

For documenting what changed between versions. Three columns: what, severity, result.

```markdown
| Change | Impact | Result |
|---|---|---|
| prompts.yaml v9→v10: Softened waiver in LIMITATIONS AND EXCEPTIONS | **Major positive** | Reduced emergency waiver over-application, +20 fields |
| fields_description.yaml: emergency_visit v8→v9, outpatient v3→v4 | **Positive** | Cleaner extraction across Anthem, UHC |
| (No golden data changes) | — | — |
```

---

## Cost Scalability Tables

Show how unit economics improve with volume. Include current state and 2-3 projections.

```markdown
| Scenario                   | Monthly Runs | AI Cost/Month | Total Cost/Run |
| -------------------------- | ------------ | ------------- | -------------- |
| Current (Connect only)     | ~41          | ~$87          | $6.86          |
| Post-Nelligan (3× volume)  | ~123         | ~$250–310     | ~$4.00–4.50    |
| Steady state (5× volume)   | ~205         | ~$410–510     | ~$3.05–3.67    |

At 5× current volume, the total cost per case drops from **$6.86 to approximately $3.35** — a 55% improvement driven by infrastructure amortization.
```

---

## Roadmap Tables

Three columns: timeline, milestone, status. Bold the upcoming items.

```markdown
| Timeline         | Milestone                                  | Status       |
| ---------------- | ------------------------------------------ | ------------ |
| Late 2025        | Platform live for Amwins Connect (Medical) | Complete     |
| Jan–Feb 2026     | Regression test harness operational        | Complete     |
| **Mar 13, 2026** | **AI Document Classifier launch**          | **On track** |
| **Mar 13, 2026** | **Nelligan division onboarding**           | **On track** |
| Q2 2026          | 85%+ extraction accuracy target            | Planned      |
```

---

## Troubleshooting Tables

For guides and runbooks. Developers scanning this table are looking for their specific error.

```markdown
| Error | Cause | Fix |
|---|---|---|
| `Table already exists` | Running migrations on a pre-Alembic DB | `alembic stamp <revision_id>` |
| `Foreign key constraint failed` during seeding | Migrations haven't run | `alembic upgrade head` first |
| Fields not appearing in DB | Model not in seed extraction | Check `seed_data.py` includes your model |
```

---

## Quick Reference Tables

Put the most common scenarios in a table at the top of developer guides — before any detailed sections.

```markdown
| Scenario | Commands |
|---|---|
| **New environment** | `cd api && python init_db.py` |
| **Existing (pre-Alembic) DB** | `cd api && alembic stamp db08502a5cf2 && python seed_data.py` |
| **Regular deployment** | `cd api && alembic upgrade head && python seed_data.py` |
```

---

## File Reference Tables

Include the file's role, not just its path.

```markdown
| File | Role |
|---|---|
| `spreader/tests/regression/results/latest.json` | Current regression results (Run 10) |
| `spreader/queue_triggered_func/config/products/medical/fields_description.yaml` | Field descriptions (emergency v9, outpatient v4) |
| `spreader/queue_triggered_func/config/products/medical/prompts.yaml` | Summary prompt (v10 — softened waiver) |
```
