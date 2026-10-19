/* KaTeX Configuration for MkDocs Material
 * Add to mkdocs.yml:
 *   extra_javascript:
 *     - javascripts/katex-config.js
 *     - https://unpkg.com/katex@0/dist/katex.min.js
 *     - https://unpkg.com/katex@0/dist/contrib/auto-render.min.js
 *   extra_css:
 *     - https://unpkg.com/katex@0/dist/katex.min.css
 *
 * Also add to markdown_extensions:
 *   - pymdownx.arithmatex:
 *       generic: true
 */

document$.subscribe(({ body }) => {
  renderMathInElement(body, {
    delimiters: [
      { left: "$$",  right: "$$",  display: true },
      { left: "$",   right: "$",   display: false },
      { left: "\\(", right: "\\)", display: false },
      { left: "\\[", right: "\\]", display: true }
    ],
    // Skip rendering in code blocks and certain elements
    ignoredTags: [
      "script", "noscript", "style", "textarea", "pre", "code", "option"
    ],
    ignoredClasses: [
      "no-katex"
    ],
    // Throw on error for debugging (set to false in production)
    throwOnError: false,
    // Enable error color for debugging
    errorColor: "#cc0000",
    // Common macros
    macros: {
      "\\RR": "\\mathbb{R}",
      "\\NN": "\\mathbb{N}",
      "\\ZZ": "\\mathbb{Z}",
      "\\QQ": "\\mathbb{Q}",
      "\\CC": "\\mathbb{C}",
      "\\vec": "\\mathbf{#1}",
      "\\norm": "\\left\\|#1\\right\\|",
      "\\abs": "\\left|#1\\right|"
    }
  });
});
