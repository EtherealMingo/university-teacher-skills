/* Quiz Functionality for MkDocs Material
 * Add to mkdocs.yml:
 *   extra_javascript:
 *     - javascripts/quiz.js
 *   extra_css:
 *     - css/quiz.css
 *
 * Usage in markdown:
 * <div class="quiz-question" data-question-id="q1">
 *   <p><strong>Question text here?</strong></p>
 *   <div class="quiz-option" data-correct="false">Option A</div>
 *   <div class="quiz-option" data-correct="true">Option B (correct)</div>
 *   <div class="quiz-option" data-correct="false">Option C</div>
 *   <div class="quiz-option" data-correct="false">Option D</div>
 *   <div class="quiz-feedback"></div>
 *   <div class="quiz-explanation">Explanation of the correct answer.</div>
 * </div>
 */

(function() {
  'use strict';

  // Track quiz state
  const quizState = {
    answered: new Set(),
    correct: 0,
    total: 0
  };

  function initQuiz() {
    const questions = document.querySelectorAll('.quiz-question');
    quizState.total = questions.length;

    questions.forEach((question, index) => {
      const questionId = question.dataset.questionId || `q${index}`;
      const options = question.querySelectorAll('.quiz-option');
      const feedback = question.querySelector('.quiz-feedback');
      const explanation = question.querySelector('.quiz-explanation');

      // Add letter labels if not present
      options.forEach((option, i) => {
        if (!option.dataset.letter) {
          option.dataset.letter = String.fromCharCode(65 + i); // A, B, C, D...
        }
      });

      options.forEach((option) => {
        option.addEventListener('click', function() {
          // Skip if already answered
          if (quizState.answered.has(questionId)) {
            return;
          }

          // Mark as answered
          quizState.answered.add(questionId);

          // Remove previous selection
          options.forEach((o) => {
            o.classList.remove('selected', 'correct', 'incorrect');
          });

          // Mark selected option
          option.classList.add('selected');

          const isCorrect = option.dataset.correct === 'true';

          if (isCorrect) {
            option.classList.add('correct');
            quizState.correct++;
            if (feedback) {
              feedback.textContent = '✓ Correct!';
              feedback.className = 'quiz-feedback correct';
            }
          } else {
            option.classList.add('incorrect');
            // Highlight the correct answer
            options.forEach((o) => {
              if (o.dataset.correct === 'true') {
                o.classList.add('correct');
              }
            });
            if (feedback) {
              feedback.textContent = '✗ Incorrect. See the correct answer highlighted above.';
              feedback.className = 'quiz-feedback incorrect';
            }
          }

          // Show explanation if present
          if (explanation) {
            explanation.classList.add('show');
          }

          // Update progress
          updateProgress();

          // Store in localStorage
          saveProgress(questionId, isCorrect);
        });
      });
    });

    // Add reset button if multiple questions
    if (questions.length > 1) {
      addProgressDisplay();
    }

    // Load saved progress
    loadProgress();
  }

  function updateProgress() {
    const progressDisplay = document.querySelector('.quiz-progress');
    if (progressDisplay) {
      const scoreSpan = progressDisplay.querySelector('.quiz-score');
      if (scoreSpan) {
        scoreSpan.textContent = `${quizState.correct} / ${quizState.answered.size} correct`;
      }
    }
  }

  function addProgressDisplay() {
    const firstQuestion = document.querySelector('.quiz-question');
    if (!firstQuestion) return;

    const progressDiv = document.createElement('div');
    progressDiv.className = 'quiz-progress';
    progressDiv.innerHTML = `
      <span>Progress: <span class="quiz-score">0 / 0 correct</span></span>
      <button class="quiz-reset">Reset Quiz</button>
    `;

    firstQuestion.parentNode.insertBefore(progressDiv, firstQuestion);

    // Reset functionality
    progressDiv.querySelector('.quiz-reset').addEventListener('click', resetQuiz);
  }

  function resetQuiz() {
    quizState.answered.clear();
    quizState.correct = 0;

    document.querySelectorAll('.quiz-question').forEach((question) => {
      const options = question.querySelectorAll('.quiz-option');
      const feedback = question.querySelector('.quiz-feedback');
      const explanation = question.querySelector('.quiz-explanation');

      options.forEach((o) => {
        o.classList.remove('selected', 'correct', 'incorrect');
      });

      if (feedback) {
        feedback.className = 'quiz-feedback';
        feedback.textContent = '';
      }

      if (explanation) {
        explanation.classList.remove('show');
      }
    });

    updateProgress();
    clearSavedProgress();
  }

  function saveProgress(questionId, isCorrect) {
    try {
      const pageKey = `quiz_${window.location.pathname}`;
      const saved = JSON.parse(localStorage.getItem(pageKey) || '{}');
      saved[questionId] = isCorrect;
      localStorage.setItem(pageKey, JSON.stringify(saved));
    } catch (e) {
      // localStorage not available
    }
  }

  function loadProgress() {
    try {
      const pageKey = `quiz_${window.location.pathname}`;
      const saved = JSON.parse(localStorage.getItem(pageKey) || '{}');

      Object.entries(saved).forEach(([questionId, isCorrect]) => {
        const question = document.querySelector(`[data-question-id="${questionId}"]`);
        if (!question) return;

        const options = question.querySelectorAll('.quiz-option');
        const feedback = question.querySelector('.quiz-feedback');
        const explanation = question.querySelector('.quiz-explanation');

        quizState.answered.add(questionId);
        if (isCorrect) quizState.correct++;

        // Find and mark the correct answer
        options.forEach((o) => {
          if (o.dataset.correct === 'true') {
            o.classList.add('correct');
          }
        });

        if (feedback) {
          feedback.textContent = isCorrect ? '✓ Correct!' : '✗ Incorrect.';
          feedback.className = `quiz-feedback ${isCorrect ? 'correct' : 'incorrect'}`;
        }

        if (explanation) {
          explanation.classList.add('show');
        }
      });

      updateProgress();
    } catch (e) {
      // localStorage not available
    }
  }

  function clearSavedProgress() {
    try {
      const pageKey = `quiz_${window.location.pathname}`;
      localStorage.removeItem(pageKey);
    } catch (e) {
      // localStorage not available
    }
  }

  // Initialize on page load and navigation
  if (typeof document$ !== 'undefined') {
    document$.subscribe(initQuiz);
  } else {
    document.addEventListener('DOMContentLoaded', initQuiz);
  }
})();
