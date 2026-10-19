# Reading Level Analysis Guide

## Overview

This guide generates a **chapter-by-chapter reading level report** for an
intelligent textbook. The report uses the Flesch-Kincaid grade level formula
to measure prose difficulty across all chapters and verify that the textbook
maintains a consistent reading level appropriate for the target audience.

## Why This Matters

When a textbook targets a specific grade level (e.g., Grade 5), every chapter
should read at roughly the same difficulty. If Chapter 3 reads at grade 4 and
Chapter 11 reads at grade 8, the student experience is inconsistent — some
chapters feel easy, others feel impossible. A reading level report catches
these inconsistencies.

The report also helps textbook authors respond to external reviewers who
suggest using reading level as a "difficulty ladder" in the learning graph.
In well-written textbooks with controlled vocabulary, reading level variation
is typically too small to be meaningful — the report provides data to support
that claim.

## Prerequisites

- An MkDocs Material intelligent textbook project with chapters in `docs/chapters/`
- Each chapter directory has an `index.md` file
- Python 3.8+
- The `textstat` library: `pip install textstat`

## Quick Start

### Step 1: Install the dependency

```bash
pip install textstat
```

### Step 2: Run the analysis script

```bash
# From the book-installer scripts directory:
python analyze-reading-levels.py /path/to/your/project

# Or specify a custom output path:
python analyze-reading-levels.py /path/to/your/project \
    --output docs/learning-graph/chapter-reading-levels.md

# Preview without writing (dry run):
python analyze-reading-levels.py /path/to/your/project --dry-run
```

### Step 3: Add to navigation

Add the report to `mkdocs.yml` under the Learning Graph section:

```yaml
  - Learning Graph:
    - ...existing entries...
    - Reading Levels: learning-graph/chapter-reading-levels.md
```

### Step 4: Verify

```bash
mkdocs serve
# Visit http://127.0.0.1:8000/<project-name>/learning-graph/chapter-reading-levels/
```

## What the Script Does

1. **Finds all chapters** in `docs/chapters/*/index.md`, sorted by chapter number
2. **Strips formatting** — removes YAML frontmatter, HTML tags, markdown syntax,
   code blocks, URLs, and list markers to isolate the prose
3. **Computes metrics** for each chapter:
   - Flesch-Kincaid grade level (the primary metric)
   - Flesch reading ease score
   - Average sentence length
   - Word count
4. **Generates a markdown report** with:
   - A per-chapter table (chapter number, title, FK grade, notes)
   - Summary statistics (mean, median, min, max, range, standard deviation)
   - An interpretation section that explains whether the variation is
     meaningful or an artifact of domain vocabulary

## Understanding the Results

### Flesch-Kincaid Grade Level

The FK formula estimates the US school grade level needed to understand the
text. It uses two inputs:

- **Average sentence length** (words per sentence)
- **Average syllables per word**

A score of 7.1 means the text is roughly at a 7th-grade reading level.

### Why Scores May Be Higher Than Expected

The FK formula penalizes multi-syllable words equally, whether they are
genuinely hard or are domain terms that the textbook carefully defines.
Words like *cyberbullying* (4 syllables), *misinformation* (6 syllables),
and *responsibility* (6 syllables) inflate the score even when the
surrounding prose is simple.

**This is expected.** A chapter about cyberbullying will always score
higher than a chapter about healthy habits because of vocabulary, not
because of harder ideas.

### What to Look For

| Metric | Healthy Range | Concern Threshold |
|--------|---------------|-------------------|
| Standard deviation | < 1.0 grade levels | > 1.5 grade levels |
| Range (max - min) | < 2.0 grade levels | > 3.0 grade levels |
| Any single chapter | Within 2 of target | > 3 above target |

If the standard deviation is below 1.0, the textbook is highly consistent
and reading level does not add a useful difficulty dimension to the
learning graph.

## Command-Line Options

| Option | Description |
|--------|-------------|
| `project_path` | (Required) Path to project root with `mkdocs.yml` |
| `--output`, `-o` | Custom output path (default: `docs/learning-graph/chapter-reading-levels.md`) |
| `--dry-run`, `-n` | Print report to stdout instead of writing a file |

## Example Output

```
Reading level report written to: docs/learning-graph/chapter-reading-levels.md

Summary:
  Chapters analyzed: 17
  Mean FK Grade: 7.1
  Range: 6.2 - 7.9
  Std Dev: 0.55
```

## Integration with Feature Checklist

The reading level report is tracked in the feature checklist as part of
the Learning Graph System. The `detect_features.py` script checks for the
file at `docs/learning-graph/chapter-reading-levels.md`.

## When to Re-Run

Re-run the analysis whenever:

- New chapters are added
- Existing chapter content is substantially rewritten
- The textbook is being evaluated for adoption by a school district
- An external reviewer questions reading level consistency
