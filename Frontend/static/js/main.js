const API_URL = 'http://localhost:5000/api/'


// === Helpers === # Pourquoi pas mettre dans un autre fichier 'helpers.js'
// **************************************************
//                  HELPERS
// **************************************************

function getHeaders(requireAuth = false) {
    const headers = { 'Content-Type': 'application/json' };

    if (requireAuth) {
        const match = document.cookie.match(new RegExp('(^| )token=([^;]+)'));
        const token = match ? match[2] : null;

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
    }

    return headers;
}

async function handleResponse(response) {
    if (!response.ok) {
        const error = await response.json().catch(() => ({
            error: `HTTP ${response.status}: ${response.statusText}`
        }));
        throw new Error(error.error || error.message || 'Erreur inconnue');
    }
    return response.json();
}

async function isLoggedIn() {
    const res = await fetch(`${API_URL}/users/me`, {
        method: "GET",
        credentials: "include"
    });

    return res.ok;
}


// **************************************************
//                  API CALLS 
// **************************************************

// *************    USERS DATA    *******************
async function fetchUser(userId) {
    try {
        const response = await fetch(`${API_URL}/users/me/users/${userId}`);

        if (!response.ok) {
            return null;
        }

        return await response.json();

    } catch (error) {
        console.error("User fetch error:", error);
        return null;
    }
}

// ===== Data =====
const flashcardsData = [
    {
        id: 1,
        question: 'What is React?',
        answer: 'React is a JavaScript library for building user interfaces, particularly single-page applications. It allows developers to create reusable UI components.',
        category: 'Frontend',
        difficulty: 'Beginner',
    },
    {
        id: 2,
        question: 'What is the Virtual DOM?',
        answer: 'The Virtual DOM is a lightweight copy of the actual DOM. React uses it to optimize updates by comparing changes and only updating what\'s necessary.',
        category: 'Frontend',
        difficulty: 'Intermediate',
    },
    {
        id: 3,
        question: 'What are React Hooks?',
        answer: 'Hooks are functions that let you use state and other React features in functional components. Common hooks include useState, useEffect, and useContext.',
        category: 'Frontend',
        difficulty: 'Intermediate',
    },
    {
        id: 4,
        question: 'What is TypeScript?',
        answer: 'TypeScript is a superset of JavaScript that adds static typing. It helps catch errors during development and improves code maintainability.',
        category: 'Languages',
        difficulty: 'Beginner',
    },
    {
        id: 5,
        question: 'What is CSS Grid?',
        answer: 'CSS Grid is a two-dimensional layout system that allows you to create complex layouts with rows and columns easily.',
        category: 'Frontend',
        difficulty: 'Intermediate',
    },
];

const quizData = [
    {
        id: 1,
        question: 'Qu\'est-ce que React?',
        options: [
            'Un framework CSS',
            'Une bibliothèque JavaScript pour construire des interfaces utilisateur',
            'Un langage de programmation',
            'Un système de base de données',
        ],
        correctAnswer: 1,
        category: 'Frontend',
    },
    {
        id: 2,
        question: 'Quel hook React est utilisé pour gérer l\'état local?',
        options: ['useEffect', 'useState', 'useContext', 'useReducer'],
        correctAnswer: 1,
        category: 'Frontend',
    },
    {
        id: 3,
        question: 'Qu\'est-ce que le Virtual DOM?',
        options: [
            'Une base de données virtuelle',
            'Une copie légère du DOM réel',
            'Un serveur virtuel',
            'Un outil de débogage',
        ],
        correctAnswer: 1,
        category: 'Frontend',
    },
    {
        id: 4,
        question: 'Quelle est la différence entre let et const?',
        options: [
            'Il n\'y a pas de différence',
            'let permet la réassignation, const non',
            'const est plus rapide',
            'let est obsolète',
        ],
        correctAnswer: 1,
        category: 'JavaScript',
    },
    {
        id: 5,
        question: 'Qu\'est-ce que TypeScript?',
        options: [
            'Un nouveau langage de programmation',
            'Un superset de JavaScript avec typage statique',
            'Une bibliothèque JavaScript',
            'Un framework backend',
        ],
        correctAnswer: 1,
        category: 'Languages',
    },
];

// ===== State =====
let activeView = 'dashboard';
let currentCardIndex = 0;
let isCardFlipped = false;
let markedCards = {};
let currentQuizQuestion = 0;
let selectedQuizAnswer = null;
let quizAnswers = new Array(quizData.length).fill(null);
let showQuizResults = false;

// ===== Menu Toggle =====switchView
const burgerBtn = document.getElementById('burgerBtn');
const menuOverlay = document.getElementById('menuOverlay');
const menuSidebar = document.getElementById('menuSidebar');
const menuCloseBtn = document.getElementById('menuCloseBtn');
const menuItems = document.querySelectorAll('.menu-item');

function openMenu() {
    menuOverlay.classList.add('active');
    menuSidebar.classList.add('active');
    const menuIcon = burgerBtn.querySelector('.menu-icon');
    const closeIcon = burgerBtn.querySelector('.close-icon');
    menuIcon.classList.add('hidden');
    closeIcon.classList.remove('hidden');
}

function closeMenu() {
    menuOverlay.classList.remove('active');
    menuSidebar.classList.remove('active');
    const menuIcon = burgerBtn.querySelector('.menu-icon');
    const closeIcon = burgerBtn.querySelector('.close-icon');
    menuIcon.classList.remove('hidden');
    closeIcon.classList.add('hidden');
}

burgerBtn.addEventListener('click', () => {
    if (menuSidebar.classList.contains('active')) {
        closeMenu();
    } else {
        openMenu();
    }
});

menuCloseBtn.addEventListener('click', closeMenu);
menuOverlay.addEventListener('click', closeMenu);

// Close menu with Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeMenu();
    }
});

// ===== Navigation =====
menuItems.forEach(item => {
    item.addEventListener('click', () => {
        const view = item.getAttribute('data-view');
        switchView(view);
        closeMenu();
    });
});

function switchView(view) {
    activeView = view;
    
    // Update menu items
    menuItems.forEach(item => {
        if (item.getAttribute('data-view') === view) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
    
    // Update view containers
    document.querySelectorAll('.view-container').forEach(container => {
        container.classList.remove('active');
    });
    
    if (view === 'dashboard') {
        document.getElementById('dashboardView').classList.add('active');
    } else if (view === 'cards') {
        document.getElementById('cardsView').classList.add('active');
        renderFlashcard();
    } else if (view === 'quiz') {
        document.getElementById('quizView').classList.add('active');
        resetQuiz();
    }
}

// ===== Logout Modal =====
const logoutBtn = document.getElementById('logoutBtn');
const logoutModal = document.getElementById('logoutModal');
const cancelLogoutBtn = document.getElementById('cancelLogoutBtn');
const confirmLogoutBtn = document.getElementById('confirmLogoutBtn');

logoutBtn.addEventListener('click', () => {
    closeMenu();
    logoutModal.classList.remove('hidden');
});

cancelLogoutBtn.addEventListener('click', () => {
    logoutModal.classList.add('hidden');
});

confirmLogoutBtn.addEventListener('click', () => {
    alert('Redirection vers la page de connexion...');
    logoutModal.classList.add('hidden');
});

logoutModal.addEventListener('click', (e) => {
    if (e.target === logoutModal) {
        logoutModal.classList.add('hidden');
    }
});

// ===== Chart.js Initialization =====
function initChart() {
    const ctx = document.getElementById('progressChart');
    if (!ctx) return;
    
    const data = [
        { day: 'Mon', cards: 28, time: 45 },
        { day: 'Tue', cards: 35, time: 52 },
        { day: 'Wed', cards: 42, time: 68 },
        { day: 'Thu', cards: 38, time: 55 },
        { day: 'Fri', cards: 48, time: 72 },
        { day: 'Sat', cards: 55, time: 85 },
        { day: 'Sun', cards: 62, time: 92 },
    ];
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.day),
            datasets: [
                {
                    label: 'Cards Reviewed',
                    data: data.map(d => d.cards),
                    borderColor: '#ff6b35',
                    backgroundColor: 'rgba(255, 107, 53, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2,
                },
                {
                    label: 'Study Time (min)',
                    data: data.map(d => d.time),
                    borderColor: '#4a90e2',
                    backgroundColor: 'rgba(74, 144, 226, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#141414',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    titleColor: '#f5f5f5',
                    bodyColor: '#f5f5f5',
                    cornerRadius: 12,
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                        drawBorder: false,
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.3)',
                        font: {
                            size: 12
                        }
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                        drawBorder: false,
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.3)',
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

// ===== Flashcard Functions =====
function getDifficultyClass(difficulty) {
    switch (difficulty) {
        case 'Beginner':
            return 'flashcard-gradient-beginner';
        case 'Intermediate':
            return 'flashcard-gradient-intermediate';
        case 'Advanced':
            return 'flashcard-gradient-advanced';
        default:
            return 'flashcard-gradient-intermediate';
    }
}

function getDifficultyBadgeClass(difficulty) {
    switch (difficulty) {
        case 'Beginner':
            return 'flashcard-difficulty-beginner';
        case 'Intermediate':
            return 'flashcard-difficulty-intermediate';
        case 'Advanced':
            return 'flashcard-difficulty-advanced';
        default:
            return 'flashcard-difficulty-intermediate';
    }
}

function renderFlashcard() {
    const card = flashcardsData[currentCardIndex];
    const progress = ((currentCardIndex + 1) / flashcardsData.length) * 100;
    
    // Update progress
    document.getElementById('cardProgress').textContent = `${currentCardIndex + 1} / ${flashcardsData.length}`;
    document.getElementById('cardProgressBar').style.width = `${progress}%`;
    
    // Update card content
    document.getElementById('cardCategory').textContent = card.category;
    document.getElementById('cardDifficulty').textContent = card.difficulty;
    document.getElementById('cardQuestion').textContent = card.question;
    document.getElementById('cardAnswer').textContent = card.answer;
    
    // Update difficulty classes
    const difficultyClass = getDifficultyClass(card.difficulty);
    const badgeClass = getDifficultyBadgeClass(card.difficulty);
    
    document.querySelectorAll('.flashcard-decorative-gradient').forEach(el => {
        el.className = 'flashcard-decorative-gradient ' + difficultyClass;
    });
    
    document.getElementById('cardDifficulty').className = 'flashcard-difficulty ' + badgeClass;
    
    // Update stats
    const correctCount = Object.values(markedCards).filter(v => v === 'correct').length;
    const incorrectCount = Object.values(markedCards).filter(v => v === 'incorrect').length;
    const remaining = flashcardsData.length - Object.keys(markedCards).length;
    
    document.getElementById('correctCount').textContent = correctCount;
    document.getElementById('incorrectCount').textContent = incorrectCount;
    document.getElementById('remainingCount').textContent = remaining;
    
    // Update buttons
    document.getElementById('prevCardBtn').disabled = currentCardIndex === 0;
    document.getElementById('nextCardBtn').disabled = currentCardIndex === flashcardsData.length - 1;
    
    // Reset flip state
    isCardFlipped = false;
    document.getElementById('flashcard').classList.remove('flipped');
    
    // Re-initialize Lucide icons
    lucide.createIcons();
}

// Flashcard flip
document.getElementById('flashcard').addEventListener('click', () => {
    isCardFlipped = !isCardFlipped;
    document.getElementById('flashcard').classList.toggle('flipped');
});

// Flashcard navigation
document.getElementById('prevCardBtn').addEventListener('click', () => {
    if (currentCardIndex > 0) {
        currentCardIndex--;
        renderFlashcard();
    }
});

document.getElementById('nextCardBtn').addEventListener('click', () => {
    if (currentCardIndex < flashcardsData.length - 1) {
        currentCardIndex++;
        renderFlashcard();
    }
});

// Mark card
document.getElementById('correctBtn').addEventListener('click', () => {
    const card = flashcardsData[currentCardIndex];
    markedCards[card.id] = 'correct';
    setTimeout(() => {
        if (currentCardIndex < flashcardsData.length - 1) {
            currentCardIndex++;
            renderFlashcard();
        }
    }, 300);
});

document.getElementById('incorrectBtn').addEventListener('click', () => {
    const card = flashcardsData[currentCardIndex];
    markedCards[card.id] = 'incorrect';
    setTimeout(() => {
        if (currentCardIndex < flashcardsData.length - 1) {
            currentCardIndex++;
            renderFlashcard();
        }
    }, 300);
});

// ===== Quiz Functions =====
function resetQuiz() {
    currentQuizQuestion = 0;
    selectedQuizAnswer = null;
    quizAnswers = new Array(quizData.length).fill(null);
    showQuizResults = false;
    
    document.getElementById('quizQuestions').classList.remove('hidden');
    document.getElementById('quizResults').classList.add('hidden');
    
    renderQuizQuestion();
}

function renderQuizQuestion() {
    const question = quizData[currentQuizQuestion];
    const progress = ((currentQuizQuestion + 1) / quizData.length) * 100;
    
    // Update progress
    document.getElementById('quizProgress').textContent = `${currentQuizQuestion + 1} / ${quizData.length}`;
    document.getElementById('quizProgressBar').style.width = `${progress}%`;
    
    // Update question
    document.getElementById('quizCategory').textContent = question.category;
    document.getElementById('quizQuestion').textContent = question.question;
    
    // Update button text
    const nextBtnText = currentQuizQuestion === quizData.length - 1 ? 'Voir les résultats' : 'Suivant';
    document.getElementById('nextBtnText').textContent = nextBtnText;
    
    // Render options
    const optionsContainer = document.getElementById('quizOptions');
    optionsContainer.innerHTML = '';
    
    question.options.forEach((option, index) => {
        const optionBtn = document.createElement('button');
        optionBtn.className = 'quiz-option';
        if (quizAnswers[currentQuizQuestion] === index) {
            optionBtn.classList.add('selected');
        }
        
        optionBtn.innerHTML = `
            <div class="quiz-option-radio">
                <div class="quiz-option-radio-inner"></div>
            </div>
            <span class="quiz-option-text">${option}</span>
        `;
        
        optionBtn.addEventListener('click', () => selectQuizAnswer(index));
        optionsContainer.appendChild(optionBtn);
    });
    
    // Update status and button
    selectedQuizAnswer = quizAnswers[currentQuizQuestion];
    updateQuizStatus();
    
    // Re-initialize Lucide icons
    lucide.createIcons();
}

function selectQuizAnswer(answerIndex) {
    selectedQuizAnswer = answerIndex;
    quizAnswers[currentQuizQuestion] = answerIndex;
    
    // Update selected state
    document.querySelectorAll('.quiz-option').forEach((btn, index) => {
        if (index === answerIndex) {
            btn.classList.add('selected');
        } else {
            btn.classList.remove('selected');
        }
    });
    
    updateQuizStatus();
}

function updateQuizStatus() {
    const statusEl = document.getElementById('quizStatus');
    const nextBtn = document.getElementById('quizNextBtn');
    
    if (selectedQuizAnswer !== null) {
        statusEl.textContent = 'Réponse sélectionnée';
        nextBtn.disabled = false;
    } else {
        statusEl.textContent = 'Sélectionnez une réponse';
        nextBtn.disabled = true;
    }
}

document.getElementById('quizNextBtn').addEventListener('click', () => {
    if (selectedQuizAnswer === null) return;
    
    if (currentQuizQuestion < quizData.length - 1) {
        currentQuizQuestion++;
        selectedQuizAnswer = quizAnswers[currentQuizQuestion];
        renderQuizQuestion();
    } else {
        showQuizResults = true;
        renderQuizResults();
    }
});

function renderQuizResults() {
    document.getElementById('quizQuestions').classList.add('hidden');
    document.getElementById('quizResults').classList.remove('hidden');
    
    // Calculate score
    const score = quizAnswers.reduce((total, answer, index) => {
        return answer === quizData[index].correctAnswer ? total + 1 : total;
    }, 0);
    
    const percentage = (score / quizData.length) * 100;
    const grade = percentage >= 70 ? 'A' : percentage >= 50 ? 'B' : 'C';
    
    // Update results
    document.getElementById('quizScoreValue').textContent = `${score} / ${quizData.length}`;
    document.getElementById('quizScorePercentage').textContent = `${percentage.toFixed(0)}% de réussite`;
    document.getElementById('quizScoreBar').style.width = `${percentage}%`;
    
    document.getElementById('quizCorrectTotal').textContent = score;
    document.getElementById('quizIncorrectTotal').textContent = quizData.length - score;
    document.getElementById('quizGrade').textContent = grade;
    
    // Render answer details
    const answersList = document.getElementById('quizAnswersList');
    answersList.innerHTML = '';
    
    quizData.forEach((question, index) => {
        const userAnswer = quizAnswers[index];
        const isCorrect = userAnswer === question.correctAnswer;
        
        const answerItem = document.createElement('div');
        answerItem.className = `quiz-answer-item ${isCorrect ? 'correct' : 'incorrect'}`;
        
        answerItem.innerHTML = `
            <div class="quiz-answer-content">
                <div class="quiz-answer-icon-wrapper ${isCorrect ? 'correct' : 'incorrect'}">
                    <i data-lucide="${isCorrect ? 'check-circle' : 'x-circle'}"></i>
                </div>
                <div class="quiz-answer-text">
                    <div class="quiz-answer-question">${question.question}</div>
                    <div class="quiz-user-answer">
                        Votre réponse: 
                        <span class="quiz-user-answer-value ${isCorrect ? 'correct' : 'incorrect'}">
                            ${userAnswer !== null ? question.options[userAnswer] : 'Pas de réponse'}
                        </span>
                    </div>
                    ${!isCorrect ? `
                        <div class="quiz-correct-answer">
                            Réponse correcte: ${question.options[question.correctAnswer]}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        answersList.appendChild(answerItem);
    });
    
    // Re-initialize Lucide icons
    lucide.createIcons();
}

document.getElementById('quizRestartBtn').addEventListener('click', resetQuiz);

// ===== Initialize App =====
document.addEventListener('DOMContentLoaded', () => {
    initChart();
    renderFlashcard();
    lucide.createIcons();
});
