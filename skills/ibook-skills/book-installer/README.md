# Book Installer Skill

Installs and configures project infrastructure for MkDocs Material intelligent textbooks.

## Quick Start

Say `book-installer help` to see all available features, then select by number or name.

## Math Equation Syntax

This skill configures KaTeX with a **currency-safe** setup. Single `$` is NOT used for inline math, so you can write dollar amounts naturally.

### Quick Reference

| What You Want | Syntax | Example |
|---------------|--------|---------|
| Inline math | `\(...\)` | `The equation \(E = mc^2\) is famous.` |
| Display math (block) | `$$...$$` | See below |
| Display math (alt) | `\[...\]` | See below |
| Currency | `$20` | `The book costs $29.99.` (no escaping needed) |

### Inline Math

Use backslash-parentheses for inline equations:

```markdown
Einstein's equation \(E = mc^2\) relates mass and energy.

The quadratic formula is \(x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}\).
```

### Display Math (Block)

Use double dollar signs or backslash-brackets for centered equations:

```markdown
The Gaussian integral:
$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$

Alternatively:
\[
\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}
\]
```

### Currency Values

Dollar signs work naturally without escaping:

```markdown
The textbook costs $89.99.
Prices range from $10 to $500.
We saved $25.00 on the purchase.
```

## Configuration Files

The math configuration requires two files:

### mkdocs.yml

```yaml
markdown_extensions:
  - pymdownx.arithmatex:
      generic: true
      inline_syntax: ['round']
      block_syntax: ['dollar', 'square']

extra_javascript:
  - js/katex.js
  - https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js
  - https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js

extra_css:
  - https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css
```

### docs/js/katex.js

```javascript
// KaTeX auto-render configuration
// Single $ is NOT used for math to allow currency notation like $20
// Use \(...\) for inline math and $$...$$ or \[...\] for display math
document.addEventListener("DOMContentLoaded", function() {
    renderMathInElement(document.body, {
        delimiters: [
            {left: "$$", right: "$$", display: true},
            {left: "\\[", right: "\\]", display: true},
            {left: "\\(", right: "\\)", display: false}
        ],
        throwOnError: false
    });
});
```

## Why This Configuration?

Many technical textbooks discuss both mathematics and costs:

- Control systems textbooks might mention "$20 Arduino boards"
- Economics courses frequently use dollar amounts
- Engineering texts reference component prices

The traditional LaTeX convention of `$...$` for inline math conflicts with currency notation. This configuration:

1. Uses `\(...\)` for inline math (LaTeX standard alternative)
2. Preserves `$$...$$` for display math (widely expected)
3. Leaves single `$` for currency (no escaping needed)

## Comparison with Standard KaTeX

| Feature | Standard KaTeX | This Configuration |
|---------|---------------|-------------------|
| Inline math | `$E=mc^2$` | `\(E=mc^2\)` |
| Display math | `$$...$$` | `$$...$$` (same) |
| Currency $20 | `\$20` (escaped) | `$20` (natural) |

## Available Features

Run `book-installer help` to see all 28+ features including:

- Project templates
- Branding (logo, favicon, cover images)
- Math equations (KaTeX or MathJax)
- Code highlighting with copy buttons
- Mermaid diagrams
- Interactive quizzes
- Learning graph viewer
- And more...

## See Also

- [MkDocs Material Documentation](https://squidfunk.github.io/mkdocs-material/)
- [KaTeX Supported Functions](https://katex.org/docs/supported.html)
- [PyMdown Arithmatex](https://facelessuser.github.io/pymdown-extensions/extensions/arithmatex/)
