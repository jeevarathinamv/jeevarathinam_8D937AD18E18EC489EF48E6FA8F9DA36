/**
 * Raja Raja Cholan Historical Information Website
 * Interactive Frontend Scripts
 * - Interactive MCQ Quiz Engine
 * - Dynamic Gallery Filtering & Modal Lightbox
 * - Admin Confirmations & Responsive Utilities
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Initialize Quiz Engine if quiz container is present
  const quizApp = document.getElementById('cholaQuizApp');
  if (quizApp) {
    initQuizEngine();
  }

  // 2. Initialize Gallery Filter if gallery container is present
  const galleryGrid = document.getElementById('cholaGalleryGrid');
  if (galleryGrid) {
    initGalleryFilter();
  }

  // 3. Auto-hide alert toasts after 4 seconds
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) {
        bsAlert.close();
      }
    }, 4500);
  });
});

/* ========================================================
   QUIZ ENGINE IMPLEMENTATION
   ======================================================== */
function initQuizEngine() {
  const questionBox = document.getElementById('quizQuestionBox');
  const optionsContainer = document.getElementById('quizOptionsContainer');
  const submitBtn = document.getElementById('quizSubmitBtn');
  const nextBtn = document.getElementById('quizNextBtn');
  const progressBar = document.getElementById('quizProgressBar');
  const currentCountElem = document.getElementById('quizCurrentCount');
  const totalCountElem = document.getElementById('quizTotalCount');
  const resultCard = document.getElementById('quizResultCard');
  const scoreText = document.getElementById('quizScoreText');
  const scorePercent = document.getElementById('quizScorePercent');
  const scoreFeedback = document.getElementById('quizScoreFeedback');
  const playAgainBtn = document.getElementById('quizPlayAgainBtn');
  const explanationBox = document.getElementById('quizExplanationBox');
  const explanationText = document.getElementById('quizExplanationText');

  let questions = [];
  let currentIndex = 0;
  let score = 0;
  let selectedOption = null;

  // Fetch questions from backend JSON API
  fetch('/api/quiz')
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success' && data.questions && data.questions.length > 0) {
        questions = data.questions;
        totalCountElem.textContent = questions.length;
        loadQuestion(0);
      } else {
        questionBox.innerHTML = '<p class="text-danger">Unable to load quiz questions at this moment.</p>';
      }
    })
    .catch(err => {
      console.error('Quiz fetch error:', err);
      questionBox.innerHTML = '<p class="text-warning">Failed to load quiz from database. Please reload the page.</p>';
    });

  function loadQuestion(index) {
    currentIndex = index;
    selectedOption = null;
    const q = questions[index];

    currentCountElem.textContent = index + 1;
    const progress = ((index) / questions.length) * 100;
    progressBar.style.width = `${progress}%`;

    questionBox.innerHTML = `<h4 class="chola-heading mb-3">${index + 1}. ${escapeHtml(q.question)}</h4>`;
    explanationBox.classList.add('d-none');
    submitBtn.classList.remove('d-none');
    submitBtn.disabled = true;
    nextBtn.classList.add('d-none');

    const options = [
      { key: 'A', text: q.option_a },
      { key: 'B', text: q.option_b },
      { key: 'C', text: q.option_c },
      { key: 'D', text: q.option_d }
    ];

    optionsContainer.innerHTML = '';
    options.forEach(opt => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'quiz-option-btn';
      btn.dataset.option = opt.key;
      btn.innerHTML = `<strong class="text-warning me-2">${opt.key}.</strong> ${escapeHtml(opt.text)}`;

      btn.addEventListener('click', function () {
        if (!submitBtn.classList.contains('d-none')) {
          document.querySelectorAll('.quiz-option-btn').forEach(b => b.classList.remove('selected'));
          btn.classList.add('selected');
          selectedOption = opt.key;
          submitBtn.disabled = false;
        }
      });

      optionsContainer.appendChild(btn);
    });
  }

  // Submit Answer
  submitBtn.addEventListener('click', function () {
    if (!selectedOption) return;

    const q = questions[currentIndex];
    const isCorrect = (selectedOption === q.correct_option);

    if (isCorrect) {
      score++;
    }

    // Highlight correct & incorrect
    document.querySelectorAll('.quiz-option-btn').forEach(btn => {
      btn.disabled = true;
      if (btn.dataset.option === q.correct_option) {
        btn.classList.add('correct');
      } else if (btn.dataset.option === selectedOption && !isCorrect) {
        btn.classList.add('incorrect');
      }
    });

    // Show Explanation
    if (q.explanation) {
      explanationText.innerHTML = (isCorrect ? '✅ <strong>Correct!</strong> ' : '❌ <strong>Incorrect!</strong> ') + escapeHtml(q.explanation);
      explanationBox.classList.remove('d-none');
    }

    submitBtn.classList.add('d-none');
    nextBtn.classList.remove('d-none');

    if (currentIndex + 1 === questions.length) {
      nextBtn.textContent = 'View Final Results';
    } else {
      nextBtn.textContent = 'Next Question →';
    }
  });

  // Next Question / Complete
  nextBtn.addEventListener('click', function () {
    if (currentIndex + 1 < questions.length) {
      loadQuestion(currentIndex + 1);
    } else {
      showFinalResults();
    }
  });

  function showFinalResults() {
    progressBar.style.width = '100%';
    document.getElementById('quizActiveCard').classList.add('d-none');
    resultCard.classList.remove('d-none');

    const total = questions.length;
    const percentage = Math.round((score / total) * 100);

    scoreText.textContent = `${score} / ${total}`;
    scorePercent.textContent = `${percentage}%`;

    if (percentage === 100) {
      scoreFeedback.innerHTML = '🏆 <strong>Imperial Gold Scholar!</strong> You possess profound knowledge of Emperor Raja Raja Cholan and Chola heritage!';
    } else if (percentage >= 70) {
      scoreFeedback.innerHTML = '🎖️ <strong>Valiant Commander!</strong> Great performance! You have a solid grasp of Chola history and Thanjavur architecture.';
    } else if (percentage >= 50) {
      scoreFeedback.innerHTML = '📜 <strong>Chola Cadet!</strong> Good attempt! Explore our history and military sections to discover more amazing facts.';
    } else {
      scoreFeedback.innerHTML = '📖 <strong>Eager Explorer!</strong> Review the timeline and articles on our site, then test your knowledge again!';
    }
  }

  // Play Again
  playAgainBtn.addEventListener('click', function () {
    score = 0;
    currentIndex = 0;
    resultCard.classList.add('d-none');
    document.getElementById('quizActiveCard').classList.remove('d-none');
    loadQuestion(0);
  });
}

/* ========================================================
   GALLERY FILTER & MODAL VIEWER
   ======================================================== */
function initGalleryFilter() {
  const filterBtns = document.querySelectorAll('.gallery-filter-btn');
  const items = document.querySelectorAll('.gallery-item');

  filterBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filter = btn.dataset.filter;
      items.forEach(item => {
        if (filter === 'all' || item.dataset.category === filter) {
          item.style.display = 'block';
        } else {
          item.style.display = 'none';
        }
      });
    });
  });

  // Gallery Modal Lightbox
  const modalImg = document.getElementById('galleryModalImage');
  const modalTitle = document.getElementById('galleryModalTitle');
  const modalDesc = document.getElementById('galleryModalDesc');
  const modalAttribution = document.getElementById('galleryModalAttribution');

  document.querySelectorAll('.gallery-card').forEach(card => {
    card.addEventListener('click', function () {
      const src = card.dataset.img;
      const title = card.dataset.title;
      const desc = card.dataset.desc;
      const attribution = card.dataset.attribution;

      if (modalImg) modalImg.src = src;
      if (modalTitle) modalTitle.textContent = title;
      if (modalDesc) modalDesc.textContent = desc;
      if (modalAttribution) modalAttribution.textContent = attribution || 'Public Domain / Historical Archive';

      const modalElem = document.getElementById('galleryLightboxModal');
      if (modalElem) {
        const bsModal = new bootstrap.Modal(modalElem);
        bsModal.show();
      }
    });
  });
}

function escapeHtml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
