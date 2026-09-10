# econ-skills

Reusable AI skills for empirical economics research. Built for
[Claude Code](https://claude.ai/code), compatible with Cursor, Cline,
and other AI coding tools.

## Install

    npx skills add eabeam/econ-skills

Or install individual skills:

    npx skills add eabeam/econ-skills --skill econ-audit
    npx skills add eabeam/econ-skills --skill data-dictionary
    npx skills add eabeam/econ-skills --skill lit-review

## Skills

### /econ-audit
Adversarial econometrics review. Checks your Stata, R, or Python
analysis code for specification errors, clustering mistakes, bad
controls, and silent analytical failures — the things that produce
wrong conclusions even when the code runs without errors.

### /data-dictionary
Auto-generates codebooks from Stata .dta files. Produces variable
lists, summary statistics, value labels, and missingness reports.
Three modes: summary, full, and analysis-ready.

### /lit-review
Structured multi-session literature review workflow. Scaffolds a
review with standardized files, tracks papers across sessions,
generates slide decks (Beamer, Quarto, or Markdown), and runs
referee passes to check for canonical paper coverage.

Run `/lit-review setup` on first use to configure.

## License

CC-BY 4.0. Built by [Emily Beam](https://eabeam.github.io),
University of Vermont.
