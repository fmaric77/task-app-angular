# Writing Pattern Examples

Concrete examples of executive summaries, metadata blocks, structural conventions, and prose patterns from production documentation.

## Contents

1. [Executive Summaries](#executive-summaries)
2. [Metadata Blocks](#metadata-blocks)
3. [Feasibility Section Headers](#feasibility-section-headers)
4. [Code-in-Context Pattern](#code-in-context-pattern)
5. [Phased Recommendations](#phased-recommendations)

---

## Executive Summaries

Deliver the conclusion first, then the evidence. Bold the key finding. Keep to 2-5 sentences for the core point.

### Technical Analysis Style

```markdown
## Executive Summary

**Run 10 crosses the 80% threshold at 81.14%** (942/1161), gaining +20 fields
and +3 passing tests over Run 9. This is a new all-time high in both accuracy
and passing tests (**9/27**).

The improvement was driven by:
1. **Prompt v10:** Softened the waiver example in LIMITATIONS AND EXCEPTIONS
   to prevent over-application of "(waived if admitted)"
2. **Further field description refinements** for emergency visit (v9),
   chiropractic/acupuncture, and outpatient surgery fields.

**Anthem surged to 83.1%** (+21 fields, +7.0pp) with 3 newly passing tests.
**UHC recovered** (+6 fields). However, **Aetna dropped** (-5 fields) and
**BSC slipped** slightly (-4 fields).

The system is now stably above 80%. The remaining gap to 85%+ is primarily
golden data format issues and a few extraction challenges.
```

**Why this works:** Leads with the headline number. Gives the delta from last run. Explains what drove the change. Calls out both winners and losers. Ends with a forward-looking assessment.

### Feasibility Style

```markdown
## Executive Summary

The database schema already supports pricing-less plans — all pricing-related
columns are nullable and no constraints require pricing data. However, the
processing pipelines, API enqueue logic, and legacy frontend all currently
**hard-require** a pricing document. Making this work is feasible but requires
targeted changes across all layers. Option processing is significantly easier
to adapt than current/renewal processing.
```

**Why this works:** States the current state ("already supports"), then the gap ("hard-require"), then the verdict ("feasible but requires targeted changes").

### Project Overview Style

```markdown
## Overview

The AI Spreadsheeting Platform is a purpose-built solution that automates the
extraction and organization of employee benefits data from insurance carrier
documents. It replaces a labor-intensive, manual process — reading PDF plan
summaries, identifying benefit values, and populating comparison spreadsheets
— with an AI-powered pipeline that performs the same work in a fraction of
the time.

The platform has been live in production for the **Amwins Connect** division
since late 2025. Expansion to the **Nelligan** division (ancillary products)
and the introduction of an **AI Document Classifier** are both targeted for
March 13, 2026.
```

**Why this works:** First paragraph says what it is and what it replaces. Second paragraph gives status and what's coming. No jargon, no setup.

---

## Metadata Blocks

Keep metadata tight. Two styles depending on formality.

### Formal (stakeholder docs)

```markdown
**Prepared for:** [Client]
**Prepared by:** Elixirr
**Date:** February 2026
**Status:** Production (Amwins Connect); Nelligan onboarding targeted March 13, 2026
```

### Technical (internal docs)

```markdown
**Date:** 2026-03-03
**Author:** Elixirr Engineering
**User Story:**

> *As a user, I want to be able to at times process documents without
> providing pricing documents, so that I can spread only the benefits
> and not the pricing.*
```

### Analysis Reports (data-heavy)

```markdown
**Run ID:** `regression-2026-02-17-180749`
**Timestamp:** 2026-02-17T18:07:49
**Report Generated:** 2026-02-17
**Product:** Medical
**Target Accuracy:** 80%+
```

**Note:** Analysis report metadata includes the machine-readable run ID for traceability.

---

## Feasibility Section Headers

Each section opens with a one-line feasibility + effort rating. This lets someone skim just the headers to get the full picture.

```markdown
## 1. Option Processing

**Feasibility: HIGH | Estimated Effort: 2–3 days**

The option processing pipeline in `processing_main.py` already has a partial
code path for a missing pricing file:
```

```markdown
## 2. Current/Renewal Processing

**Feasibility: MEDIUM-LOW | Estimated Effort: 5–8 days**

Current/renewal processing is structurally more tightly coupled to pricing.
```

---

## Code-in-Context Pattern

Always include the file path and approximate line number as a comment. Show only the relevant excerpt.

````markdown
The processor hard-raises if no pricing file is present:

```python
# process_renewal.py ~line 779
else:
    raise FileNotFoundError(
        f"No pricing PDF or Excel file found in '{pricing_folder}'."
    )
```

Unlike option processing, there is no graceful fallback at all.
````

Then follow with a changes-required table:

```markdown
### Changes Required

| File | Change | Complexity |
|---|---|---|
| `processing_main.py` → `process_folder` | Route into benefits-only mode instead of returning `None` | Medium |
| `function_app.py` | Handle absent `pricing_doc` in queue message; skip download | Low |
```

**Why this works:** Code shows exactly what the current behavior is. Table tells exactly what needs to change and how hard it is.

---

## Phased Recommendations

End feasibility studies with a numbered phase plan. Include a gate for later phases.

```markdown
## Recommendation

This feature is **feasible and sensible for option processing**. Recommended
approach:

1. **Phase 1:** Implement for option processing (~1 sprint). Low risk, clear
   scope.
2. **Phase 2 (if needed):** Extend to current/renewal processing. Requires a
   design decision on what a "benefits-only renewal spread" looks like in the
   output, since pricing is currently a structural part of the renewal output
   object.

Before committing to Phase 2, confirm with stakeholders whether benefits-only
renewal spreads are a genuine use case or whether the value of current/renewal
processing is primarily the pricing comparison.
```
