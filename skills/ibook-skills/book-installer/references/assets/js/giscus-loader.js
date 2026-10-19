/* Giscus Comments Loader for MkDocs Material
 * Add to mkdocs.yml:
 *   extra_javascript:
 *     - javascripts/giscus-loader.js
 *
 *   extra:
 *     giscus:
 *       repo: "username/repo-name"
 *       repo_id: "R_xxxxx"
 *       category: "Announcements"
 *       category_id: "DIC_xxxxx"
 *       mapping: "pathname"
 *       reactions_enabled: "1"
 *       emit_metadata: "0"
 *       input_position: "top"
 *       theme: "preferred_color_scheme"
 *       lang: "en"
 *
 * Get your repo_id and category_id from: https://giscus.app
 */

(function() {
  'use strict';

  function initGiscus() {
    // Don't add comments to certain pages
    const excludedPaths = ['/search/', '/tags/', '/404.html', '/$'];
    if (excludedPaths.some(path => {
      if (path === '/$') {
        return window.location.pathname === '/' || window.location.pathname.endsWith('/index.html');
      }
      return window.location.pathname.includes(path);
    })) {
      return;
    }

    // Check if giscus already exists
    if (document.querySelector('.giscus')) {
      return;
    }

    const content = document.querySelector('.md-content__inner');
    if (!content) return;

    // Get configuration from MkDocs
    const config = getGiscusConfig();
    if (!config.repo || !config.repoId) {
      console.warn('Giscus: Missing required configuration (repo, repo_id)');
      return;
    }

    // Create container
    const container = document.createElement('div');
    container.className = 'giscus-container';
    container.style.marginTop = '2rem';
    content.appendChild(container);

    // Create and configure script
    const script = document.createElement('script');
    script.src = 'https://giscus.app/client.js';
    script.dataset.repo = config.repo;
    script.dataset.repoId = config.repoId;
    script.dataset.category = config.category || 'Announcements';
    script.dataset.categoryId = config.categoryId;
    script.dataset.mapping = config.mapping || 'pathname';
    script.dataset.strict = config.strict || '0';
    script.dataset.reactionsEnabled = config.reactionsEnabled || '1';
    script.dataset.emitMetadata = config.emitMetadata || '0';
    script.dataset.inputPosition = config.inputPosition || 'top';
    script.dataset.theme = getGiscusTheme(config.theme);
    script.dataset.lang = config.lang || 'en';
    script.crossOrigin = 'anonymous';
    script.async = true;

    container.appendChild(script);

    // Handle theme changes
    observeThemeChanges(config.theme);
  }

  function getGiscusConfig() {
    // Try to get config from MkDocs
    try {
      // MkDocs Material stores config in __md_get
      if (typeof __md_get !== 'undefined') {
        const extra = __md_get('__extra') || {};
        return extra.giscus || {};
      }
    } catch (e) {
      // Config not available
    }

    // Fallback: try to get from data attributes on body
    const body = document.body;
    return {
      repo: body.dataset.giscusRepo,
      repoId: body.dataset.giscusRepoId,
      category: body.dataset.giscusCategory,
      categoryId: body.dataset.giscusCategoryId,
      mapping: body.dataset.giscusMapping,
      theme: body.dataset.giscusTheme,
      lang: body.dataset.giscusLang
    };
  }

  function getGiscusTheme(configTheme) {
    if (configTheme && configTheme !== 'preferred_color_scheme') {
      return configTheme;
    }

    // Detect current theme from MkDocs Material
    const palette = document.body.dataset.mdColorScheme;
    if (palette === 'slate') {
      return 'dark';
    }
    return 'light';
  }

  function observeThemeChanges(configTheme) {
    if (configTheme && configTheme !== 'preferred_color_scheme') {
      return; // Fixed theme, no need to observe
    }

    // Watch for theme changes
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.attributeName === 'data-md-color-scheme') {
          const iframe = document.querySelector('.giscus-frame');
          if (iframe) {
            const theme = getGiscusTheme(configTheme);
            iframe.contentWindow.postMessage(
              { giscus: { setConfig: { theme } } },
              'https://giscus.app'
            );
          }
        }
      });
    });

    observer.observe(document.body, {
      attributes: true,
      attributeFilter: ['data-md-color-scheme']
    });
  }

  // Initialize on page load and navigation
  if (typeof document$ !== 'undefined') {
    document$.subscribe(initGiscus);
  } else {
    document.addEventListener('DOMContentLoaded', initGiscus);
  }
})();
