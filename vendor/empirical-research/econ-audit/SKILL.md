---
name: econ-audit
description: Adversarial econometrics review — catches specification errors, clustering mistakes, bad controls, and silent analytical failures in Stata, R, or Python code
---

# Econ Audit — Adversarial Econometrics Review

*v1.0 — Adversarial reviewer that catches econometric specification errors, estimation mistakes, and silent analytical failures. Asks: "Will this produce correct economic conclusions?"*

Review econometric code (Stata, R, or Python) for specification errors, estimation mistakes, and analytical choices that could produce wrong conclusions — even when the code runs without errors. This is the "hostile referee" for your analysis code.

**Argument:** `$ARGUMENTS`
- Path to a file (`.do`, `.R`, `.py`) or a directory

**Modes** (append to argument):
- `spec` (default) — Single-file specification review: clustering, controls, functional form, sample
- `full` — Deep review with project context: reads data documentation, related files, pre-analysis plan
- `compare` — Compare two specification files or pre/post versions for specification drift

**Flags:**
- `pap:path/to/pap.pdf` — Compare against a pre-analysis plan
- `vars:outcome1,outcome2` — Focus audit on specific outcome variables
- `design:rct|did|iv|rd|panel` — Specify research design (auto-detected if omitted)
- `severity:high` — Only report high-severity issues

Example: `/econ-audit code/analysis/02_main_results.do`
Example: `/econ-audit ./my-project full design:rct`
Example: `/econ-audit my_regs.do pap:pre_analysis_plan.pdf`
Example: `/econ-audit old_spec.do compare new_spec.do`

---

## Instructions

### Step 0: Locate Code and Context

1. Resolve `$ARGUMENTS` to find the target file(s):
   - If a file path: read that file directly
   - If a directory: search it for analysis-stage files
   - If a bare name: search the current working directory and immediate subdirectories (`code/`, `analysis/`, `dofiles/`)
   - Glob for analysis-stage files: `*regress*`, `*analysis*`, `*results*`, `*estimate*`, `*main*`
2. Read the project's `CLAUDE.md`, `README.md`, or similar context file if available — look for:
   - Research design (RCT, DiD, IV, RD, panel)
   - Treatment variable names
   - Primary outcome variables
   - Clustering structure (individual, household, village, school, etc.)
   - Pre-analysis plan references
3. If `full` mode: also read:
   - Data cleaning code to understand variable construction
   - Master do-file for pipeline context
   - Any `.pdf` or `.md` file containing "pre-analysis plan", "PAP", or "protocol"
   - Variable labels or codebook if available
4. If `pap:` flag provided: read the PAP and extract registered specifications

Detect language from file extension. Parse mode, flags, and design from `$ARGUMENTS`.

**Auto-detect research design** if not specified:
- Look for `treatment`, `treat`, `T`, `arm` variables → likely RCT
- Look for `post`, `time`, `after` interacted with group → likely DiD
- Look for `ivregress`, `ivreg2`, `2sls` → likely IV
- Look for `rd`, `bandwidth`, `running variable`, `cutoff` → likely RD
- Look for `xtreg`, `xtset`, `plm`, `fe` → likely panel

---

### Step 1: Clustering and Standard Errors

**This is the single most common source of wrong inference in applied economics.**

#### 1.1 Clustering Level
- **Identify the level of treatment assignment** (individual, household, village, district, school, etc.)
- **Check that standard errors are clustered at or above the level of treatment assignment**
  - Flag: `reg y treatment, robust` when treatment is assigned at village level (needs `cluster(village)`)
  - Flag: `reg y treatment, cluster(household)` when treatment is assigned at village level (clustered too low)
  - Flag: Clustering at a level below treatment assignment in ANY regression
- **For DiD**: Check clustering is at the unit level (not time), per Bertrand, Duflo & Mullainathan (2004)
- **For multi-level designs**: Check whether two-way clustering is needed (e.g., `cluster(village year)`)

#### 1.2 Few Clusters
- Count or estimate the number of clusters from context/documentation
- Flag if likely < 50 clusters without small-sample correction (wild cluster bootstrap, CR2/CR3 standard errors)
- Flag if clustering variable has suspiciously low cardinality

#### 1.3 Standard Error Consistency
- Flag if standard error specification changes across regressions in the same file without explanation
- Flag if some regressions use `robust` and others use `cluster()` on the same sample
- Flag `vce(robust)` used with `reghdfe` absorbing group fixed effects (should cluster at absorbed level)

#### 1.4 Heteroskedasticity
- Flag OLS with `reg y x` (no `robust` or `vce()` at all) — almost never appropriate in applied work
- Exception: Explicitly homoskedastic models (rare, must be justified)

---

### Step 2: Variable Interpretation and Construction

#### 2.1 Treatment Variable
- Verify treatment variable is binary (0/1) or correctly coded for multi-arm
- Flag if treatment variable appears to be continuous but is used as binary (or vice versa)
- Flag if treatment = ITT assignment is confused with actual take-up (TOT)
- Flag if treatment variable has missing values that silently drop observations
- For multi-arm trials: flag if all arms are pooled without testing for differential effects (unless justified)

#### 2.2 Outcome Variables
- Flag outcome variables used in levels when logs would be standard (income, expenditure, wages) — or vice versa
- Flag outcomes that appear to be indices but are used without documentation of construction method
- Flag if an outcome is a rate/ratio but the denominator could be zero or missing
- Flag binary outcomes estimated with OLS without noting LPM choice (not necessarily wrong, but should be acknowledged)

#### 2.3 Control Variables
- **Bad controls (Angrist & Pischke)**: Flag controls that are themselves affected by treatment (post-treatment variables, mediators)
  - Pattern: `reg y treatment post_treatment_var` where `post_treatment_var` could be on the causal path
  - Common culprits: current income in education RCT, current employment in training program, attitudes in information experiment
- **Collider bias**: Flag conditioning on a variable that is a common effect of treatment and outcome
- **Kitchen sink**: Flag specifications with >15 controls without justification or discussion of over-controlling

#### 2.4 Variable Confusion
- Flag if variable names suggest one thing but usage suggests another (e.g., `age` used as a year, `income_monthly` summed as annual)
- Flag if the same variable name appears with different transformations across specifications without noting which is which
- Flag log transformations applied to variables that can be zero or negative without `log(x + 1)` or IHS or noting the issue

---

### Step 3: Specification and Functional Form

#### 3.1 Core Specification Check
- **RCT**: Verify the basic spec is `Y = a + b*Treatment + controls + e`
  - Flag if stratification/randomization controls are missing (strata fixed effects, baseline value of outcome)
  - Flag if baseline covariates included for balance are not the same across specifications
- **DiD**: Verify includes unit FE + time FE + interaction
  - Flag if parallel trends assumption is untestable and not discussed
  - Flag vanilla two-way FE with staggered treatment without acknowledging Goodman-Bacon / Sun & Abraham / Callaway & Sant'Anna concerns
- **IV**: Check first stage is reported, F-stat is reported, exclusion restriction is discussed
  - Flag if first-stage F < 10 without weak instrument discussion
  - Flag if number of instruments > number of endogenous variables without overidentification test
- **RD**: Check bandwidth selection method, kernel choice, and polynomial order
  - Flag polynomial order > 2 (Gelman & Imbens 2019)
  - Flag if McCrary/manipulation test not mentioned
  - Flag if multiple bandwidths not shown for robustness

#### 3.2 Fixed Effects
- Flag if individual/unit fixed effects absorb the variation of interest (e.g., individual FE in cross-sectional treatment effect)
- Flag if time fixed effects absorb a common treatment timing (all treated at same time + year FE = no identification)
- Flag `areg` or manual demeaning when `reghdfe` would be more appropriate and handle singletons
- Flag if fixed effects are included in some specs but not others without discussion

#### 3.3 Interaction Terms
- Flag interaction `treatment#X` without the constituent terms (main effects)
- Flag interpretation of interaction coefficients in non-linear models (logit/probit) without noting marginal effects issue
- Flag triple interactions without clear justification and discussion of interpretation

#### 3.4 Functional Form
- Flag linear probability models for outcomes near 0 or 1 (predictions outside [0,1] likely)
- Flag log-level or level-log specifications where the interpretation doesn't match the narrative
- Flag quadratic terms without checking whether the turning point is in-sample

---

### Step 4: Sample and Selection

#### 4.1 Sample Consistency
- **Flag if the sample changes across specifications** without explicit documentation
  - Different `if` conditions across regressions
  - Different `keep`/`drop` statements
  - Missingness on different control variables shrinking the sample
- Flag if the number of observations changes across columns of what should be the same table
- Verify N is reported or calculable for every regression

#### 4.2 Attrition and Selection
- For RCTs: flag if attrition is not addressed (Lee bounds, attrition table, or discussion)
- Flag if sample restrictions could induce selection bias (e.g., dropping based on a post-treatment variable)
- Flag `drop if missing(x)` for multiple variables without checking whether missingness is differential by treatment

#### 4.3 Outlier Treatment
- Flag if outliers are dropped or winsorized asymmetrically (top only, or at different percentiles for treatment vs control)
- Flag if winsorization thresholds are not reported
- Flag if results are shown only with winsorized data and not also with raw data (or vice versa)
- Flag if outlier treatment differs across specifications without explanation

---

### Step 5: Imputation and Missing Data

**"Aggressive imputations when not asked" is a specific concern — pay close attention.**

#### 5.1 Unauthorized Imputation
- Flag ANY imputation that is not explicitly documented or justified:
  - `replace x = 0 if missing(x)` — replacing missing with zero is an imputation
  - `mvencode _all, mv(0)` — blanket missing-to-zero is almost always wrong
  - `ipolate` or `mipolate` without documentation
  - Mean/median imputation without flagging the imputed observations
- Flag if imputation inflates the sample size relative to what documentation says
- Flag if imputed values are used in regressions without sensitivity analysis

#### 5.2 Imputation That Changes Results
- Flag if imputation systematically affects one group more than another (differential imputation by treatment arm)
- Flag if the imputation assumption (e.g., missing = zero) favors the hypothesis
- Flag `replace x = 0 if missing(x)` for consumption/expenditure variables (zeros vs. truly missing are economically different)

#### 5.3 Missing Data Handling
- Flag if missing data is handled by listwise deletion without noting sample size implications
- Flag if missing indicators ("missing flags") are included as controls (Angrist & Pischke warn against this)
- Flag if different missing data approaches are used for different variables without justification

---

### Step 6: Multiple Hypothesis Testing

#### 6.1 Multiple Outcomes
- Count the number of distinct outcome variables tested
- Flag if >3 primary outcomes without multiple testing correction (Bonferroni, Holm, FDR/BH, FWER)
- Flag if "families" of outcomes are tested without family-wise correction
- Check if a pre-analysis plan specifies primary vs. secondary outcomes — flag deviations

#### 6.2 Subgroup Analysis
- Flag extensive subgroup analysis without pre-registration or correction
- Flag if subgroups are defined using post-treatment variables
- Flag "treasure hunting" patterns: many subgroups tested, only significant ones reported

#### 6.3 Specification Searching
- Flag if many specifications are estimated but only a subset are reported
- Flag if the reported specification is an unusual combination of controls/sample/FE
- Flag if robustness checks all fail but the main result is presented without caveat

---

### Step 7: Weights and Survey Design

#### 7.1 Sampling Weights
- Flag if the study uses survey data but `[pw=]` or `[aw=]` or `svyset` is absent
- Flag if weights are used in some specifications but not others without explanation
- Flag if `pweight` vs `aweight` vs `fweight` choice is not discussed
- Flag `fweight` used for sampling weights (common mistake — `fweight` is for frequency, not probability)

#### 7.2 Survey Design
- Flag if `svyset` stratification/clustering differs from the regression's `cluster()` option
- Flag if survey design is ignored in subgroup analyses

---

### Step 8: Dropped Variables and Observations (full mode)

*Enhanced checks in `full` mode — requires reading data cleaning code.*

#### 8.1 Variable Tracking
- If cleaning code is available: trace which variables from raw data make it to the analysis dataset
- Flag variables that are constructed in cleaning but never used in analysis (may be forgotten outcomes)
- Flag variables that appear in the PAP but are absent from the analysis dataset
- Flag outcome variables that were renamed between cleaning and analysis in ways that could cause confusion

#### 8.2 Observation Tracking
- Trace sample size from raw data to analysis: how many observations are lost at each step?
- Flag any step that drops >10% of observations without explicit justification
- Flag if the final analysis sample is <80% of the eligible sample without an attrition discussion
- Compare sample size in regressions to expected sample size from documentation/PAP

---

### Step 9: PAP Compliance (when pap: flag provided)

*Skip unless `pap:` flag is set.*

#### 9.1 Registered Specifications
- Extract primary specifications from the PAP
- Compare each registered specification to what is actually estimated
- Flag deviations: different controls, different functional form, different sample, different clustering
- Flag outcomes in the PAP that are not analyzed
- Flag outcomes analyzed that are not in the PAP (mark as exploratory)

#### 9.2 Registered Hypotheses
- Check that the direction of hypothesized effects matches what is tested
- Check that primary vs. secondary distinction is maintained
- Flag if the paper's framing doesn't match the PAP's framing

---

### Step 10: Generate Report

**Save report to the same directory as the reviewed file:**
`econ_audit_[filename]_[YYYY-MM-DD].md`

For project-level reviews:
`econ_audit_[project]_[YYYY-MM-DD].md`

**Classify each finding by severity:**
- **CRITICAL** — Will produce wrong inference. Standard errors are wrong, causal claims are invalidated, or conclusions don't follow from the analysis. Fix before any presentation or submission.
- **HIGH** — Significant risk of wrong inference. Specification choice is questionable, an important robustness check is missing, or a key assumption is untested. Fix before submission.
- **MEDIUM** — Analytical choice that should be justified or tested. May be intentional but needs documentation. Address in revision.
- **LOW** — Minor issue or suggestion. Standard practice but not strictly necessary.

Tell the user the full path to the output file.

---

## Output Format

```markdown
# Econ Audit: [filename or project name]

**Date:** [YYYY-MM-DD]
**Mode:** [spec / full / compare]
**Language:** [Stata / R / Python]
**Detected design:** [RCT / DiD / IV / RD / Panel / Cross-sectional]
**File(s) reviewed:** [path(s)]
**Reviewer:** /econ-audit v1.0

---

## Summary

**Overall assessment:** [Sound / Minor Issues / Needs Revision / Significant Concerns]
**Findings:** [N] critical, [N] high, [N] medium, [N] low

[2-3 sentence summary. Lead with the most important finding. State the design and whether the core identification strategy appears correctly implemented.]

---

## Identification & Design Assessment

[Brief assessment of whether the research design is correctly implemented in the code. This is the most important section.]

- **Treatment variable:** [name] — [assessment]
- **Clustering:** [level used] — [correct/incorrect and why]
- **Core specification:** [description] — [assessment]
- **Key assumption(s):** [parallel trends / exclusion restriction / continuity / etc.] — [tested? how?]

---

## Critical & High Findings

### F1: [Title]
- **Severity:** [CRITICAL / HIGH]
- **Category:** [Clustering / Specification / Controls / Sample / Imputation / Multiple Testing / Weights / Variable Construction / PAP Deviation]
- **Location:** [file:line_number]
- **Issue:** [What's wrong — be specific about the econometric problem]
- **Consequence:** [What goes wrong in the results — direction of bias if known]
- **Fix:** [Specific recommendation with code example if applicable]
- **Reference:** [Relevant methodological citation if applicable]

[Repeat for each critical/high finding]

---

## Medium Findings

### F[N]: [Title]
- **Severity:** MEDIUM
- **Category:** [category]
- **Location:** [location]
- **Issue:** [description]
- **Consequence:** [what could go wrong]
- **Fix:** [recommendation]

---

## Low Findings

- **F[N]:** [location] — [issue] → [recommendation]

---

## Specification Summary Table

| Spec | Outcome | Treatment | Controls | FE | Clustering | N | Flags |
|------|---------|-----------|----------|----|-----------|----|-------|
| (1) | [var] | [var] | [list] | [list] | [level] | [N] | [any] |
| (2) | ... | ... | ... | ... | ... | ... | ... |

---

## Audit Checklist

| Check | Status | Notes |
|-------|--------|-------|
| Clustering at correct level | [PASS/FAIL/WARN] | [details] |
| No bad controls | [PASS/FAIL/WARN] | [details] |
| Standard errors specified | [PASS/FAIL/WARN] | [details] |
| Treatment variable correct | [PASS/FAIL/WARN] | [details] |
| Sample consistent across specs | [PASS/FAIL/WARN] | [details] |
| No unauthorized imputation | [PASS/FAIL/WARN] | [details] |
| Multiple testing addressed | [PASS/FAIL/WARN/NA] | [details] |
| Weights appropriate | [PASS/FAIL/WARN/NA] | [details] |
| PAP compliance | [PASS/FAIL/WARN/NA] | [details] |
| Functional form appropriate | [PASS/FAIL/WARN] | [details] |
| Fixed effects correct | [PASS/FAIL/WARN/NA] | [details] |
| Outlier treatment documented | [PASS/FAIL/WARN/NA] | [details] |

---

## Next Steps

1. [Highest-priority fix]
2. [Second priority]
3. [Third priority]
```

---

## Principles

- **Inference over aesthetics.** A beautifully formatted do-file that clusters at the wrong level is worse than ugly code with correct standard errors. Always prioritize findings that affect statistical inference and causal conclusions.
- **Adversarial, not adversary.** Think like the hostile referee who will find the weakest link. Every flag is something a reviewer could raise — better to find it now.
- **Econometrics-aware.** This is not generic code review. Understand that clustering matters, that bad controls bias estimates, that missing data isn't just a nuisance. Apply the Angrist & Pischke / MHE / Mostly Harmless mental model.
- **Direction of bias when possible.** Don't just say "this is wrong" — say whether it biases toward or away from finding an effect, or whether the direction is ambiguous. This is what makes the audit actionable.
- **Ask, don't assume.** Unusual specifications may be intentional. If a choice is defensible but non-standard, flag it as "Verify: is this intentional?" with an explanation of the risk, not "Bug: this is wrong."
- **No scope creep into code quality.** Do not review variable naming, indentation, or commenting — that's what `/code-review` is for. Stay focused on whether the analysis will produce correct conclusions.
- **No data review.** Do not review distributions, outliers in the data, or data integrity — that's what `/pipeline-audit` is for. Review the *choices made in the analysis code*.
- **Cite your reasoning.** When flagging a methodological issue, reference the relevant paper or textbook concept (e.g., "Bertrand, Duflo & Mullainathan 2004" for clustering in DiD, "Angrist & Pischke Ch. 3" for bad controls). This gives the user a way to evaluate your claim.
