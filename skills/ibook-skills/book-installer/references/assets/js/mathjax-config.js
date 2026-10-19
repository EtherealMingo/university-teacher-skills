/* MathJax Configuration for MkDocs Material
 * Add to mkdocs.yml:
 *   extra_javascript:
 *     - javascripts/mathjax-config.js
 *     - https://unpkg.com/mathjax@3/es5/tex-mml-chtml.js
 *
 * Also add to markdown_extensions:
 *   - pymdownx.arithmatex:
 *       generic: true
 */

window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true,
    tags: 'ams',  // Enable equation numbering
    macros: {
      // Add common macros here
      RR: "\\mathbb{R}",
      NN: "\\mathbb{N}",
      ZZ: "\\mathbb{Z}",
      QQ: "\\mathbb{Q}",
      CC: "\\mathbb{C}",
      vec: ["\\mathbf{#1}", 1],
      norm: ["\\left\\|#1\\right\\|", 1],
      abs: ["\\left|#1\\right|", 1]
    }
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex"
  },
  chtml: {
    scale: 1,
    minScale: 0.5,
    matchFontHeight: true,
    mtextInheritFont: true
  },
  svg: {
    fontCache: 'global'
  }
};

// Re-render MathJax when page changes (for instant navigation)
document$.subscribe(() => {
  MathJax.startup.output.clearCache();
  MathJax.typesetClear();
  MathJax.texReset();
  MathJax.typesetPromise();
});
