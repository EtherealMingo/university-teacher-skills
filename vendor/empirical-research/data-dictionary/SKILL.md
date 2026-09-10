---
name: data-dictionary
description: Auto-generate comprehensive codebooks from Stata .dta files — variable lists, summary statistics, value labels, and missingness reports
---

# Data Dictionary Generator

*v1.0 — Auto-generate comprehensive codebooks from .dta files*

Read Stata .dta files and produce a structured markdown data dictionary with variable names, types, labels, value labels, summary statistics, and missingness. Outputs a ready-to-use codebook document.

**Argument:** `$ARGUMENTS`
- Path to a .dta file or directory containing .dta files

**Modes** (append to argument):
- `summary` (default) — One-page overview: variable list with types, labels, missingness
- `full` — Comprehensive codebook: summary + value labels + summary stats + distributions for key variables
- `analysis` — Analysis-ready: full + notes on which variables are outcomes vs controls, indices vs components

**Flags:**
- `vars:consumption,assets` — Only document variables matching these patterns
- `output:path/to/output.md` — Custom output path (default: same directory as input, named `codebook_[filename].md`)
- `format:md` (default) | `format:csv` — Output format

Example: `/data-dictionary data/for_analysis/endline_analysis.dta full`
Example: `/data-dictionary . vars:consumption,exp_`
Example: `/data-dictionary data/for_analysis/ summary`

---

## Instructions

### Step 0: Locate and Load Data

1. Resolve `$ARGUMENTS` to find .dta file(s):
   - If a file path: read that file directly
   - If a directory: glob for `*.dta` files in it
   - If a bare name: search the current working directory and subdirectories (`data/`, `data/for_analysis/`, `output/`)
2. For directories with many files (>10), generate an index page + individual codebooks
3. Parse mode and flags from `$ARGUMENTS`. Default to `summary`.

### Step 1: Extract Metadata

Write a temporary Python script (use `uv run python` or `python3`). Never use `python -c`.

```python
import pandas as pd
import pyreadstat

df, meta = pyreadstat.read_dta("path/to/file.dta",
                                apply_value_formats=False)

# Available metadata:
# meta.column_names          — variable names (list)
# meta.column_labels          — variable labels (dict: name -> label)
# meta.variable_value_labels  — value label mappings (dict: name -> {code: label})
# meta.original_variable_types — Stata storage types (dict: name -> type string)
# meta.number_columns         — count of numeric columns
# meta.number_rows            — row count
# meta.file_label              — dataset label
# meta.notes                   — dataset notes
```

For each variable, extract:
- **Name**: column name
- **Label**: from `meta.column_labels` (may be empty)
- **Type**: from `meta.original_variable_types` (e.g., `float`, `double`, `byte`, `int`, `long`, `str#`)
- **Value labels**: from `meta.variable_value_labels` (categorical mappings)
- **N non-missing**: count of non-null values
- **N missing**: count of null values
- **Missing %**: percentage missing
- **Unique values**: nunique

### Step 2: Summary Statistics (full and analysis modes)

For numeric variables:
- Mean, SD, Min, P25, Median, P75, Max
- Flag: negative values in typically-positive variables

For string variables:
- Number of unique values
- Top 5 most frequent values with counts
- Max string length

For binary (0/1) variables:
- Proportion = 1 (with count)

For categorical variables (those with value labels):
- Frequency table: code, label, count, percentage

### Step 3: Variable Classification (analysis mode only)

Attempt to classify variables by role based on naming patterns:

| Pattern | Classification |
|---------|---------------|
| `hhid`, `id`, `*_id` | Identifier |
| `treat*`, `arm*`, `t_*` | Treatment |
| `strat*`, `block*`, `pair*` | Stratification |
| `i_*`, `idx_*`, `index_*` | Index/Composite |
| `z_*` | Z-score |
| `exp_*`, `cons_*`, `income_*` | Outcome (economic) |
| `is_*`, `has_*`, `any_*` | Binary indicator |
| `mi_*`, `miss_*` | Missing flag |
| `_wins`, `_w`, `_tr` | Winsorized/trimmed |
| `bl_*`, `base_*` | Baseline |
| `wt_*`, `weight*` | Sampling weight |

Present classifications as suggestions, not assertions. Include an "Unclassified" category.

### Step 4: Cross-Variable Relationships (analysis mode only)

- **Index decomposition**: For index variables (i_*, idx_*), identify likely component variables and report correlations
- **Treatment balance**: If treatment variable detected, report mean of key variables by treatment arm (first 10 numeric variables)
- **Missing patterns**: Identify clusters of variables with correlated missingness

### Step 5: Generate Output

**Output location:**
- Default: same directory as input file, named `codebook_[filename]_[YYYY-MM-DD].md`
- Override with `output:` flag
- For directory inputs: `codebook_index_[YYYY-MM-DD].md` + individual codebooks

Tell the user the full absolute path to the output file.

---

## Output Format — Summary Mode

```markdown
# Data Dictionary: [filename]

**Generated:** [YYYY-MM-DD]
**Source:** [full path]
**Dataset label:** [meta.file_label if available]
**Observations:** [N rows]
**Variables:** [N columns]

---

## Variable List

| # | Variable | Label | Type | Non-missing | Missing % | Unique |
|---|----------|-------|------|-------------|-----------|--------|
| 1 | hhid | Household ID | long | 5,000 | 0.0% | 5,000 |
| 2 | treat | Treatment arm | byte | 5,000 | 0.0% | 3 |
| ... | ... | ... | ... | ... | ... | ... |

---

## Variables Without Labels

[List any variables that have no label — these may need documentation]

---

## Notes

- [N] variables are entirely missing (0 non-missing values)
- [N] variables have >50% missing values
- [N] categorical variables have value labels defined
```

## Output Format — Full Mode

Adds to summary:

```markdown
---

## Summary Statistics — Numeric Variables

| Variable | N | Mean | SD | Min | P25 | Median | P75 | Max |
|----------|---|------|-----|-----|-----|--------|-----|-----|
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

---

## Summary Statistics — Binary Variables

| Variable | Label | N | Prop = 1 | Count = 1 |
|----------|-------|---|----------|-----------|
| ... | ... | ... | ... | ... |

---

## Value Labels — Categorical Variables

### [variable_name]: [label]

| Code | Label | Count | Percent |
|------|-------|-------|---------|
| 0 | Control | 2,500 | 50.0% |
| 1 | Treatment | 2,500 | 50.0% |

[Repeat for each categorical variable with value labels]

---

## String Variables

| Variable | Label | N | Unique | Max Length | Top Values |
|----------|-------|---|--------|------------|------------|
| ... | ... | ... | ... | ... | [val1 (N), val2 (N), ...] |

---

## High Missingness Variables (>20%)

| Variable | Label | Missing % | Non-missing N |
|----------|-------|-----------|---------------|
| ... | ... | ... | ... |
```

## Output Format — Analysis Mode

Adds to full:

```markdown
---

## Variable Classification (suggested)

### Identifiers
| Variable | Label |
|----------|-------|
| hhid | Household ID |

### Treatment & Stratification
| Variable | Label | Values |
|----------|-------|--------|
| treat | Treatment arm | 0: Control, 1: Treatment |

### Outcome Indices
| Variable | Label | Mean | SD | Likely Components |
|----------|-------|------|-----|-------------------|
| i_consumption | Consumption index | 0.00 | 1.00 | exp_food, exp_nonfood, ... |

### Outcome Variables
[table]

### Control Variables / Baseline
[table]

### Missing Flags
[table]

### Unclassified
[table]

---

## Treatment Balance (first 10 numeric variables)

| Variable | Control Mean | Treatment Mean | Diff | p-value |
|----------|-------------|----------------|------|---------|
| ... | ... | ... | ... | ... |
```

---

## Principles

- **Comprehensive but scannable.** The dictionary should work as both a reference document (ctrl+F for a variable) and a quick overview (scan the summary table).
- **Metadata-first.** Always use Stata's own metadata (labels, value labels, types) rather than inferring. Only infer when metadata is missing.
- **Flag gaps.** Unlabeled variables, undocumented value labels, and high missingness are all worth flagging — they're the most likely sources of confusion.
- **Analysis mode is suggestive, not prescriptive.** Variable classification is based on naming patterns and may be wrong. Present as suggestions.
- **Reproducible.** The output includes the source path and generation date so it's clear what version of the data was documented.
