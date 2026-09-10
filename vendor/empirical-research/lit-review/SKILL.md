---
name: lit-review
description: Structured multi-session literature review workflow — scaffolds reviews, tracks papers, generates slide decks or documents, and runs referee passes for canonical paper coverage
---

# Literature Review

*v1.0 — Structured literature review workflow with multi-session continuity*

Manage literature reviews for research projects: scaffold new reviews, continue existing ones, or check status across all reviews. Reviews follow a standardized template and support multiple output formats (Markdown, Quarto, Beamer).

**Argument:** `$ARGUMENTS`
- `setup` = first-run configuration
- No argument or `status` = show status dashboard of all reviews
- `new [name]` = scaffold a new review (e.g., `new remote-ed`)
- `[name]` = continue an existing review (e.g., `soft-skills`)
- `[name] referee` = run a referee pass on an existing review

---

## Instructions

### Step 0: Read Configuration

1. Check if `~/.config/lit-review/config.yml` exists.

2. **If config does not exist and `$ARGUMENTS` is not `setup`:**
   Tell the user: "No configuration found. Run `/lit-review setup` to get started." Then stop.

3. **If config does not exist and `$ARGUMENTS` is `setup`:**
   Proceed to **Mode S**.

4. **If config exists:** Read it and extract:
   - `base_dir` — where reviews are stored
   - `author` — name for slide/document headers
   - `voice_file` — optional path to a writing voice `.md` file (null = use default)
   - `output_format` — `markdown`, `quarto`, or `beamer`

5. If `voice_file` is set and the file exists, read it. Otherwise use the default voice: clear, direct academic prose.

6. If `[base_dir]/BEST_PRACTICES.md` exists, read it for conventions.

7. Route to the appropriate mode based on `$ARGUMENTS`.

---

## Mode S: Setup (`setup`)

### S1. Ask configuration questions

Ask the user these 4 questions (can be conversational or sequential):

1. **Where should reviews be stored?** (absolute path, e.g., `~/research/literature-reviews`)
2. **What name should appear on slide/document headers?** (e.g., `Jane Smith`)
3. **Do you have a writing voice file?** (path to a `.md` file describing your preferred academic writing style, or skip)
4. **What output format do you prefer?** (`markdown`, `quarto`, or `beamer` — default: `markdown`)

### S2. Create config file

```bash
mkdir -p ~/.config/lit-review
```

Write `~/.config/lit-review/config.yml`:
```yaml
# lit-review configuration
# Created [DATE]

base_dir: [user's answer]
author: [user's answer]
voice_file: [path or null]
output_format: [markdown|quarto|beamer]
```

### S3. Create base directory and starter files

```bash
mkdir -p [base_dir]
```

Create `[base_dir]/BEST_PRACTICES.md` with the following content:

````markdown
# Literature Reviews — Best Practices

*Lessons learned from building structured, multi-session literature reviews.*

---

## What works well

### 1. Standardized folder structure

Every review uses the same template. This means anyone (or any agent) can pick up any review cold and know exactly where to look:

```
[review-name]/
├── AGENT_INSTRUCTIONS.md    # What this review is about
├── RESEARCH_QUESTIONS.md    # What we're trying to learn
├── MASTER_LIST.md           # What we've found (single source of truth)
├── SEARCH_PROCESS.md        # How we searched (databases, terms, criteria)
├── [name]_lit.bib           # Machine-readable citations
├── literature_review.*      # The deliverable (.md, .qmd, or .tex)
├── CONTINUATION_LOG.md      # What's been done / what's next
└── pdfs/                    # Full-text papers
```

This consistency is the single biggest accelerator. A new review can be built from scratch in one session because the structure is predictable.

### 2. The "Roadmap to Paper" framing

Every review starts with a table mapping **paper sections -> literature streams -> key papers**. This keeps the entire review anchored to its purpose: supporting a specific paper. The "-> Paper" callouts throughout make it easy to see how each piece of literature connects to what you're writing.

### 3. Referee pass as a final step

After the initial build, doing a "referee pass" — asking "what would a reviewer at [target journal] expect to see?" — consistently catches 5-15 foundational papers that weren't in the initial search. These tend to be canonical theory papers or seminal empirical work that reviewers treat as table stakes.

### 4. MASTER_LIST as the single source of truth

Tracking every paper in one markdown table with columns for Author, Year, Title, Key finding, and In bib makes it easy to see gaps and avoid duplicates. The "Papers to obtain" section at the bottom is a useful running to-do list.

### 5. Continuation logs enable multi-session work

The dated log entries with "What was done / What's next / Blockers" format means context doesn't get lost between sessions. This is critical when reviews span multiple days or when different agents pick up the work.

### 6. Key Takeaways sections

Adding a "Key Takeaways" section at the end of each Part forces synthesis rather than just summarization. These are the most useful for actual paper-writing because they distill what the literature means for your paper.

---

## What could be improved

### 1. PDF collection is the weakest link

The `pdfs/` folders tend to be sparse. Many papers are behind paywalls. Without full-text access, deep dives are based on abstracts and prior knowledge rather than careful reading. This is the biggest quality gap.

### 2. Bib files need a clear convention

If a paper already has a `.bib` file, create a supplementary bib for new references only. If no paper `.bib` exists, create a standalone bib. Decide this at review creation time and document it in AGENT_INSTRUCTIONS.md.

### 3. Deep dives could go deeper

Reviews tend to summarize papers well but rarely go into methodology details, effect sizes with confidence intervals, or careful comparison of estimates across studies. Full-text PDFs help enormously here.

---

## Suggestions for future reviews

### Process improvements

1. **Start with source documents when possible.** Reviews with paper drafts are much more targeted than reviews built from verbal descriptions. Even a rough 2-page outline with key citations dramatically improves quality.

2. **Do the referee pass early, not just at the end.** Foundational papers should be in the first search round. Consider starting with: "What 10 papers would a reviewer at [target journal] definitely expect to see?"

3. **Consider a two-pass approach.** First pass: broad coverage. Second pass: deep dives on the 5-10 most important papers with methodology, effect sizes, and direct comparison to your study.

4. **Add a "Positioning" section.** Explicitly state: "Here is where our paper fits in this literature, and here is what is new." This is different from "contributions" — it's about the intellectual neighborhood.

5. **Standardize diagrams.** Mermaid diagrams for experimental design or conceptual frameworks are useful — make them a standard component.

6. **Add a "Comparison Table."** A table comparing your study to the 3-5 closest papers on key dimensions (sample size, setting, design, outcomes, findings) is almost always useful for positioning.

---

## What you (the human) can do to make this more effective

### Before a session

1. **Provide the paper draft and/or PAP.** This is the single highest-leverage input. Even an incomplete draft with a bibliography gives the agent a massive head start.
2. **Point to the `.bib` file explicitly.** And specify whether it's read-only or editable.
3. **Name the target journal.** This shapes the referee pass.
4. **Flag any papers you already know are missing.** This focuses the search rather than making the agent guess.
5. **Specify read/write permissions clearly.** This avoids the risk of accidentally modifying shared files.

### During a session

6. **Drop PDFs into the `pdfs/` folder.** If you have Zotero or institutional access, exporting key PDFs between sessions would dramatically improve deep-dive quality.
7. **React to the deliverable, not just the master list.** The output file is the deliverable; the master list is bookkeeping. "Part III is too thin" is more actionable than "find more papers."

### After a session

8. **Render the output locally.** Check formatting — tables and diagrams can break in ways that aren't visible in raw source. Report any rendering issues in the next session.
9. **Update the continuation log if you do manual work.** If you add papers, edit the review, or download PDFs between sessions, note it in the log so the next session doesn't duplicate effort.

### Structural suggestions

10. **Consider a shared Zotero export.** If you're running multiple reviews, a Zotero collection exported to BibTeX + PDF folder per review is the gold standard.
11. **A "seed papers" convention.** Before starting a new review, list the 5-10 papers you consider most important. This anchors search and ensures the review reflects your intellectual priorities.

---

## Quick-start checklist for a new review

```
[ ] Create folder: [base_dir]/[name]/
[ ] Create subfolder: [base_dir]/[name]/pdfs/
[ ] Provide source documents (paper draft, PAP, existing bib)
[ ] Specify: target journal, read/write permissions, key gaps to fill
[ ] Agent creates: AGENT_INSTRUCTIONS.md, RESEARCH_QUESTIONS.md, SEARCH_PROCESS.md
[ ] Agent searches and builds: MASTER_LIST.md, [name]_lit.bib
[ ] Agent builds: literature_review.* (output file in configured format)
[ ] Referee pass: add foundational papers
[ ] Agent updates: CONTINUATION_LOG.md, SEARCH_PROCESS.md
[ ] Human: render output, drop PDFs, review and iterate
```

---

*This is a living document. Update it as patterns emerge.*
````

Create `[base_dir]/README.md`:

```markdown
# Literature Reviews

| Review | Topic | Sources | Last Session | Status |
|--------|-------|---------|--------------|--------|
```

### S4. Report

```
### Setup Complete

**Config**: ~/.config/lit-review/config.yml
**Reviews directory**: [base_dir]
**Output format**: [format]
**Files created**: BEST_PRACTICES.md, README.md

Ready to start. Run `/lit-review new [name]` to scaffold your first review.
```

---

## Mode A: Status Dashboard (no argument, or `status`)

### A1. Scan all review folders

List all subdirectories in `[base_dir]`. For each review folder, read:
- `CONTINUATION_LOG.md` — most recent entry (date + what's next)
- `MASTER_LIST.md` — count sources in the main tables
- `AGENT_INSTRUCTIONS.md` — extract topic

### A2. Display dashboard

```
## LITERATURE REVIEW STATUS — [DATE]

| Review | Topic | Sources | Last Session | Status |
|--------|-------|---------|--------------|--------|
| [name] | [topic from AGENT_INSTRUCTIONS] | [count] | [date] | [inferred] |
| ... | | | | |

### What's Next (by review)
- **[name]**: [items from continuation log]
- ...
```

### A3. Prompt

```
Options:
  [name]       — continue a review (e.g., "soft-skills")
  new [name]   — scaffold a new review
  done         — exit
```

---

## Mode B: Continue Existing Review (`[name]`)

### B1. Read review context

Read these files for `[name]` (in parallel):
1. `[base_dir]/[name]/AGENT_INSTRUCTIONS.md` — scope, themes, source documents
2. `[base_dir]/[name]/CONTINUATION_LOG.md` — where we left off
3. `[base_dir]/[name]/RESEARCH_QUESTIONS.md` — RQ structure and paper mapping
4. `[base_dir]/[name]/MASTER_LIST.md` — current source inventory

If any file is missing, flag it and offer to create it from the standard template.

### B2. Present continuation summary

Display:
```
## [REVIEW NAME] — Continuing

**Topic**: [from AGENT_INSTRUCTIONS]
**Last session**: [date from continuation log]
**Sources tracked**: [count from MASTER_LIST]

### Where we left off
[What's next items from most recent continuation log entry]

### Blockers from last session
[Any blockers noted]
```

Then ask:
```
What would you like to work on?
  1. Search for new papers (web search + forward/backward citation)
  2. Build or extend the output file (slides/document)
  3. Deep dive on specific papers (requires PDFs)
  4. Update MASTER_LIST and .bib
  5. Referee pass (check for foundational/canonical papers)
  6. Generate PDF download list (DOI links for papers missing PDFs)
  7. Something else — describe what you need
```

### B3. Execute the work

Follow the user's direction. For each work type:

**Search for new papers:**
- Use web search to find papers matching the review's research questions
- For each paper found: extract author, year, title, key finding, RQ mapping
- Check against MASTER_LIST to avoid duplicates
- **Cross-review dedup**: Also scan MASTER_LIST.md in all *other* review folders under `[base_dir]`. If a paper already exists in another review, note it: "Also in: [other-review] (RQ X.Y)". This surfaces shared intellectual territory and prevents redundant search effort.
- Add new entries to MASTER_LIST.md
- Add BibTeX entries to `[name]_lit.bib`
- Update `SEARCH_PROCESS.md` with search terms, databases used, and date
- Report: "Found N new papers. Added to MASTER_LIST and .bib. [M papers also appear in other reviews.]"

**Build/extend the output file:**
- Follow the standard structure from BEST_PRACTICES.md:
  - Roadmap (lit streams -> paper sections, key papers table)
  - Parts I-VI: thematic blocks
  - Deep dives on key papers (methodology, effect sizes, connection to paper)
  - Key Takeaways at end of each part
  - **Comparison Table** (standard component — see template below)
  - **Positioning section**: "Here is where our paper fits; here is what is new"
  - Part VII: Gaps, contributions, positioning
- Use callouts marked `-> Paper` for drafting connections
- Use Mermaid diagrams for conceptual frameworks
- Follow the voice file if configured, otherwise use clear, direct academic prose

**Comparison Table template** (include in every review, typically in Part VII or after deep dives):
```markdown
## How Our Study Compares

| Dimension | [Our study] | [Closest paper 1] | [Closest paper 2] | [Closest paper 3] |
|-----------|------------|-------------------|-------------------|-------------------|
| **Setting** | | | | |
| **Sample** | | | | |
| **Design** | | | | |
| **Treatment/Signal** | | | | |
| **Key outcomes** | | | | |
| **Main finding** | | | | |
| **What's different** | *Our contribution* | | | |

> **-> Paper**: This table maps directly to the "Contribution" section. Each row in "What's different" is a talking point.
```

**Deep dive on papers:**
- Check `pdfs/` folder for available full-text PDFs
- For each paper: methodology, sample, key results with effect sizes, limitations
- Map findings to research questions
- Note connections to the parent paper's design/framing

**Update MASTER_LIST and .bib:**
- Reconcile any papers in the output file that aren't in MASTER_LIST
- Ensure all MASTER_LIST entries have RQ mappings
- Check .bib for completeness (DOIs, journal names, page numbers)

**Referee pass:**
- See Mode D below.

**Generate PDF download list:**
- Scan MASTER_LIST.md for all papers where the PDF? column is empty, "No", or missing
- For each paper missing a PDF:
  - Look up the DOI from the .bib file (if available)
  - Construct a Google Scholar search URL: `https://scholar.google.com/scholar?q=[author]+[year]+[title keywords]`
  - Construct a DOI link: `https://doi.org/[DOI]` (if DOI available)
- Output a checklist file at `[base_dir]/[name]/PDF_DOWNLOAD_LIST.md`:

```markdown
# PDF Download List — [name]
*Generated [DATE]. [N] papers missing PDFs out of [M] total.*

Download PDFs and save to `pdfs/` using naming convention: `Author-Year-ShortTitle.pdf`

## Priority (key papers for deep dives)
- [ ] **Author Year** — Title
  - DOI: [https://doi.org/10.xxxx](https://doi.org/10.xxxx)
  - Scholar: [search](https://scholar.google.com/scholar?q=...)
  - Save as: `Author-Year-ShortTitle.pdf`

## Other papers
- [ ] **Author Year** — Title
  - Scholar: [search](...)
  - Save as: `Author-Year-ShortTitle.pdf`
```

- Report: "Generated download list: [N] papers need PDFs. [K] have DOI links, [J] have Scholar links only. File saved to `PDF_DOWNLOAD_LIST.md`."

### B4. Update continuation log

**REQUIRED at end of every session.** Add a dated entry to `CONTINUATION_LOG.md`:

```markdown
### [DATE] — [Brief description of session]

**What was done**
- [Specific accomplishments — be precise]

**What's next**
- [ ] [Actionable items]

**Blockers**
- [Any issues, or "None."]
```

### B5. Session complete report

```
### Session Complete

**Review**: [name]
**Papers added this session**: N
**Output sections added/modified**: N

Next steps: [top 2-3 items from continuation log]
```

If the output format is `quarto`, add: "Run `quarto render literature_review.qmd` to check formatting."
If the output format is `beamer`, add: "Run `pdflatex literature_review.tex` and `bibtex literature_review` to check formatting."

---

## Mode C: New Review (`new [name]`)

### C1. Gather information

Ask the user:

1. **What research project does this support?** (paper title, project name)
2. **Do you have source documents?** (paper draft, PAP, existing .bib — provide paths)
3. **What's the target journal?** (shapes the referee pass)
4. **What are the key literature streams?** (3-8 themes)
5. **Any specific gaps you know about?** (topics the lit review should focus on)

### C2. Create folder structure

```bash
mkdir -p [base_dir]/[name]/pdfs
```

### C3. Scaffold files

Create all files from the standard template. The first 6 files are common to all output formats:

**AGENT_INSTRUCTIONS.md** — Populate with:
- Topic, scope, audience
- Parent project and paper reference
- Source document paths (paper draft, PAP, .bib)
- Target journal
- Content themes (from user input)
- PDF naming convention: `Author-Year-ShortTitle.pdf`
- Before/after session checklist

**RESEARCH_QUESTIONS.md** — Populate with:
- 5-8 thematic groups of 3-5 questions each
- Mapping table: Paper element -> Literature focus
- Based on: paper draft (if available), user-specified themes, target journal expectations
- If no paper draft: create placeholder RQs from themes, mark as "Draft — refine with source documents"

**MASTER_LIST.md** — Populate with:
- Seed papers section (extracted from paper draft/.bib if available)
- Empty sections for: web search results, papers to obtain
- Column headers: Author, Year, Title, Key finding, RQ(s), In bib, PDF?

**[name]_lit.bib** — Populate with:
- BibTeX entries for seed papers (if source .bib provided)
- Otherwise: empty file with header comment

**SEARCH_PROCESS.md** — Scaffold with:
```markdown
# Search Process — [name]

*Documentation of search methodology for reproducibility.*

## Databases Searched
- [ ] Google Scholar
- [ ] NBER Working Papers
- [ ] EconLit / JSTOR
- [ ] SSRN
- [ ] Web of Science
- [ ] Other: ___

## Search Terms

| Search round | Date | Terms | Database | Results reviewed | Papers added |
|-------------|------|-------|----------|-----------------|--------------|
| 1 | [DATE] | [terms] | [database] | [N] | [M] |

## Inclusion Criteria
- [Define based on scope from AGENT_INSTRUCTIONS.md]

## Exclusion Criteria
- [Define based on scope]

## Forward/Backward Citation Searches
| Seed paper | Direction | Papers found |
|-----------|-----------|-------------|

## Notes
- [Any deviations from search plan, surprises, or methodological notes]
```

**CONTINUATION_LOG.md** — First entry:
```markdown
### [DATE] — Initial scaffold

**What was done**
- Created review folder and all template files (including SEARCH_PROCESS.md)
- [If source docs available: Extracted N seed papers from paper draft/.bib]
- [If source docs available: Drafted research questions based on paper structure]

**What's next**
- [ ] Review and approve research questions (RESEARCH_QUESTIONS.md)
- [ ] Web search for papers across all RQ themes
- [ ] Build MASTER_LIST with initial sources
- [ ] Begin output file (Part I)

**Blockers**
- [Any missing source documents or unclear scope]
```

**Format-specific output file** — depends on the `output_format` setting in config:

If `markdown`:
```markdown
# Literature Review: [Title]

*Author: [author from config]*
*Last updated: [DATE]*

## Roadmap

| Paper Section | Literature Stream | Key Papers |
|--------------|-------------------|------------|
| [placeholder] | [placeholder] | [placeholder] |

## Part I: [First literature stream]

[Placeholder slides/sections with Key Takeaways]

## Part II: [Second literature stream]

[Placeholder]

...

## How Our Study Compares

[Comparison table placeholder]

## Positioning

*Where our paper fits in this literature and what is new.*

## Gaps and Contributions

[Placeholder]

## References
```

If `quarto`:
```yaml
---
title: "Literature Review: [Title]"
subtitle: "[Subtitle based on themes]"
author: "[author from config]"
date: today
format:
  revealjs:
    theme: default
    slide-number: true
    preview-links: auto
bibliography: [name]_lit.bib
---
```
Then scaffold with: Roadmap slide, Part sections for each literature stream (placeholder slides with Key Takeaways), Comparison Table slide, Positioning slide, Part VII: Gaps and contributions, Bibliography reference.

If `beamer`:
```latex
\documentclass[aspectratio=169]{beamer}
\usetheme{metropolis}
\usepackage{natbib}
\usepackage{booktabs}
\usepackage{graphicx}

\title{Literature Review: [Title]}
\subtitle{[Subtitle based on themes]}
\author{[author from config]}
\date{\today}

\begin{document}

\maketitle

\section{Roadmap}
% Roadmap frame: lit streams -> paper sections

\section{[First literature stream]}
% Placeholder frames with Key Takeaways

\section{[Second literature stream]}
% Placeholder frames

\section{Comparison}
% How Our Study Compares table

\section{Positioning}
% Where our paper fits

\section{Gaps and Contributions}
% Placeholder

\begin{frame}[allowframebreaks]{References}
\bibliographystyle{apalike}
\bibliography{[name]_lit}
\end{frame}

\end{document}
```

### C4. Read source documents (if provided)

If the user provided a paper draft:
- Read it (respecting file permissions — .tex, .md, .pdf are OK; do not open .dta, .csv, .sav)
- Extract: research questions, cited papers, key themes, methodology, contribution claims
- Use extracted info to populate RESEARCH_QUESTIONS.md and seed the MASTER_LIST

If the user provided an existing .bib:
- Read it
- Extract entries for the MASTER_LIST seed papers section
- If read-only: note in AGENT_INSTRUCTIONS.md that a supplementary bib is needed

### C5. Update README

Add the new review to the Active Reviews table in `[base_dir]/README.md`.

### C6. Report

```
### New Review Scaffolded: [name]

**Files created**: [N] (standard template + [format] output)
**Seed papers**: N (from source documents)
**Research questions**: N themes, M questions

**Review before proceeding:**
- [ ] RESEARCH_QUESTIONS.md — approve or refine RQs
- [ ] AGENT_INSTRUCTIONS.md — check scope and themes

Ready to start searching? Run `/lit-review [name]` to begin.
```

---

## Mode D: Referee Pass (`[name] referee`)

### D1. Read review context

Same as B1 — read all review files.

### D2. Identify the target journal

From AGENT_INSTRUCTIONS.md. If not specified, ask the user.

### D3. Check for foundational papers

Ask: "What would a reviewer at [target journal] definitely expect to see cited?"

Search for canonical papers in each literature stream. Common categories:
- **Foundational theory**: Seminal theoretical models in the field
- **Seminal empirical**: Field-specific landmark studies
- **Key methodological**: Design-relevant references (e.g., methodological innovations used in the paper)
- **Recent high-profile**: Papers in top journals from last 3 years on the same topic

### D4. Cross-check against MASTER_LIST (with cross-review dedup)

For each foundational paper identified:
- Check if already in this review's MASTER_LIST
- **Cross-review check**: Also scan MASTER_LIST.md in all other review folders under `[base_dir]`. If the paper exists elsewhere, note: "Also in: [other-review]" — this can help identify shared foundational literature and avoid redundant deep dives.
- If missing from this review: add to MASTER_LIST with RQ mapping
- Add BibTeX entry to .bib
- Flag in a "Referee Pass Additions" section

### D5. Report

```
### Referee Pass Complete: [name]

**Target journal**: [journal]
**Papers checked**: N foundational/canonical papers
**Already in review**: M
**Added**: K new papers

**New additions:**
- [Author Year] — [why a reviewer would expect this]
- ...

**Potential gaps remaining:**
- [Any areas where coverage is thin]
```

Update CONTINUATION_LOG.md with referee pass results.

---

## Error Handling

- **Config not found**: "No configuration found at `~/.config/lit-review/config.yml`. Run `/lit-review setup` to create one."
- **Review folder not found**: "No review found at `[base_dir]/[name]/`. Did you mean one of: [list existing reviews]? Or run `/lit-review new [name]` to create one."
- **Missing files in existing review**: "The [name] review is missing [file]. Would you like me to create it from the standard template?"
- **No source documents for new review**: Proceed with placeholder RQs and empty MASTER_LIST. Note in CONTINUATION_LOG that source documents are needed for better targeting.
- **PDF not available for deep dive**: "Full text not available in pdfs/. Working from abstract and prior knowledge. For richer analysis, drop the PDF into `[base_dir]/[name]/pdfs/[Author-Year-ShortTitle].pdf`."

---

## Conventions

- **File naming**: lowercase with hyphens, no spaces
- **PDF naming**: `Author-Year-ShortTitle.pdf`
- **Writing voice**: Follow voice file if configured; otherwise use clear, direct academic prose
- **Citations**: BibTeX in .bib; consistent Author (Year) in prose; DOI links when available
- **Bib convention**: If paper has its own read-only .bib, create a supplementary bib for new references only
- **Continuation log**: REQUIRED after every session — date, what was done, what's next, blockers
- **MASTER_LIST as SSOT**: Every paper tracked here; no duplicates; RQ mappings for all entries
- **Search documentation**: Update SEARCH_PROCESS.md with terms, databases, and dates for every search session
- **Cross-review dedup**: When adding papers, check MASTER_LIST files in other reviews to flag shared literature
