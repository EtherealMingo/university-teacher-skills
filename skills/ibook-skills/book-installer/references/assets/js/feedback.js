/* Simple Page Feedback for MkDocs Material
 * Add to mkdocs.yml:
 *   extra_javascript:
 *     - javascripts/feedback.js
 *   extra_css:
 *     - css/feedback.css
 *
 * Optional: Configure analytics endpoint in extra:
 *   extra:
 *     feedback:
 *       endpoint: "https://your-analytics-endpoint.com/feedback"
 */

(function() {
  'use strict';

  function initFeedback() {
    // Don't add feedback to certain pages
    const excludedPaths = ['/search/', '/tags/', '/404.html'];
    if (excludedPaths.some(path => window.location.pathname.includes(path))) {
      return;
    }

    // Check if feedback already exists
    if (document.querySelector('.page-feedback')) {
      return;
    }

    const content = document.querySelector('.md-content__inner');
    if (!content) return;

    // Create feedback widget
    const feedback = document.createElement('div');
    feedback.className = 'page-feedback';
    feedback.innerHTML = `
      <p>Was this page helpful?</p>
      <button class="feedback-btn yes" data-value="yes" aria-label="Yes, this page was helpful">
        👍 Yes
      </button>
      <button class="feedback-btn no" data-value="no" aria-label="No, this page was not helpful">
        👎 No
      </button>
      <span class="feedback-thanks">Thanks for your feedback!</span>
      <div class="feedback-form">
        <textarea placeholder="How can we improve this page? (optional)" rows="3"></textarea>
        <button type="button">Submit Feedback</button>
      </div>
    `;

    content.appendChild(feedback);

    // Handle feedback clicks
    const yesBtn = feedback.querySelector('.feedback-btn.yes');
    const noBtn = feedback.querySelector('.feedback-btn.no');
    const thanks = feedback.querySelector('.feedback-thanks');
    const form = feedback.querySelector('.feedback-form');

    function handleFeedback(value) {
      // Hide buttons
      yesBtn.style.display = 'none';
      noBtn.style.display = 'none';

      if (value === 'no') {
        // Show feedback form for negative feedback
        form.classList.add('show');
      } else {
        // Show thanks for positive feedback
        thanks.classList.add('show');
      }

      // Send feedback
      sendFeedback(value);

      // Store in localStorage to prevent repeated feedback
      try {
        localStorage.setItem(`feedback_${window.location.pathname}`, value);
      } catch (e) {
        // localStorage not available
      }
    }

    yesBtn.addEventListener('click', () => handleFeedback('yes'));
    noBtn.addEventListener('click', () => handleFeedback('no'));

    // Handle form submission
    const submitBtn = form.querySelector('button');
    const textarea = form.querySelector('textarea');

    submitBtn.addEventListener('click', () => {
      const comment = textarea.value.trim();
      if (comment) {
        sendFeedback('no', comment);
      }
      form.classList.remove('show');
      thanks.classList.add('show');
    });

    // Check if already submitted feedback for this page
    try {
      const previousFeedback = localStorage.getItem(`feedback_${window.location.pathname}`);
      if (previousFeedback) {
        yesBtn.style.display = 'none';
        noBtn.style.display = 'none';
        thanks.textContent = 'You already provided feedback. Thank you!';
        thanks.classList.add('show');
      }
    } catch (e) {
      // localStorage not available
    }
  }

  function sendFeedback(value, comment = '') {
    const data = {
      page: window.location.pathname,
      url: window.location.href,
      value: value,
      comment: comment,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent
    };

    // Log to console for debugging
    console.log('Page Feedback:', data);

    // Send to Google Analytics if available
    if (typeof gtag !== 'undefined') {
      gtag('event', 'page_feedback', {
        'event_category': 'feedback',
        'event_label': window.location.pathname,
        'value': value === 'yes' ? 1 : 0
      });

      if (comment) {
        gtag('event', 'feedback_comment', {
          'event_category': 'feedback',
          'event_label': window.location.pathname
        });
      }
    }

    // Send to custom endpoint if configured
    // Check if endpoint is defined in page config
    const config = window.__md_get_config ? window.__md_get_config() : {};
    const endpoint = config?.extra?.feedback?.endpoint;

    if (endpoint) {
      fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      }).catch(err => {
        console.warn('Failed to send feedback:', err);
      });
    }
  }

  // Initialize on page load and navigation
  if (typeof document$ !== 'undefined') {
    document$.subscribe(initFeedback);
  } else {
    document.addEventListener('DOMContentLoaded', initFeedback);
  }
})();
