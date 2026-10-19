/* Copy Button for Admonitions (especially Prompt type)
 * Add to mkdocs.yml:
 *   extra_javascript:
 *     - javascripts/copy-admonition.js
 *   extra_css:
 *     - css/custom-admonitions.css
 *
 * Usage in markdown:
 * !!! prompt "Example Prompt"
 *
 *     Your prompt text here that users can copy.
 */

(function() {
  'use strict';

  function initCopyAdmonitions() {
    // Select admonitions that should have copy functionality
    const copyableTypes = ['prompt', 'example', 'code'];
    const selector = copyableTypes.map(type => `.admonition.${type}`).join(', ');

    document.querySelectorAll(selector).forEach((admonition) => {
      // Skip if already has a copy button
      if (admonition.querySelector('.admonition-copy-btn')) {
        return;
      }

      // Create copy button
      const btn = document.createElement('button');
      btn.className = 'admonition-copy-btn';
      btn.textContent = 'Copy';
      btn.setAttribute('aria-label', 'Copy content to clipboard');

      btn.addEventListener('click', async () => {
        // Get the content (everything after the title)
        const title = admonition.querySelector('.admonition-title');
        let content = '';

        // Get all content nodes after the title
        let sibling = title ? title.nextElementSibling : admonition.firstElementChild;
        while (sibling) {
          if (!sibling.classList.contains('admonition-copy-btn')) {
            content += sibling.textContent + '\n';
          }
          sibling = sibling.nextElementSibling;
        }

        content = content.trim();

        if (content) {
          try {
            await navigator.clipboard.writeText(content);
            btn.textContent = 'Copied!';
            btn.classList.add('copied');

            setTimeout(() => {
              btn.textContent = 'Copy';
              btn.classList.remove('copied');
            }, 2000);
          } catch (err) {
            console.error('Failed to copy:', err);
            btn.textContent = 'Failed';
            setTimeout(() => {
              btn.textContent = 'Copy';
            }, 2000);
          }
        }
      });

      // Position the admonition for absolute positioning of button
      admonition.style.position = 'relative';
      admonition.appendChild(btn);
    });
  }

  // Initialize on page load and navigation
  if (typeof document$ !== 'undefined') {
    document$.subscribe(initCopyAdmonitions);
  } else {
    document.addEventListener('DOMContentLoaded', initCopyAdmonitions);
  }
})();
