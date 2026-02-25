const API_URL = 'http://localhost:5000/api/'


// ===== State =====
let activeView = 'dashboard';
let currentCardIndex = 0;
let isCardFlipped = false;
let markedCards = {};
let currentQuizQuestion = 0;
let selectedQuizAnswer = null;
let showQuizResults = false;

// ===== Initialize App =====
document.addEventListener('DOMContentLoaded', () => {
    // Menu elements
    const burgerBtn = document.getElementById('burgerBtn');
    const menuOverlay = document.getElementById('menuOverlay');
    const menuSidebar = document.getElementById('menuSidebar');
    const menuCloseBtn = document.getElementById('menuCloseBtn');
    const menuItems = document.querySelectorAll('.menu-item');

    if (burgerBtn && menuOverlay && menuSidebar) {
        function openMenu() {
            menuOverlay.classList.add('active');
            menuSidebar.classList.add('active');
            const menuIcon = burgerBtn.querySelector('.menu-icon');
            const closeIcon = burgerBtn.querySelector('.close-icon');
            if (menuIcon) menuIcon.classList.add('hidden');
            if (closeIcon) closeIcon.classList.remove('hidden');
        }

        function closeMenu() {
            menuOverlay.classList.remove('active');
            menuSidebar.classList.remove('active');
            const menuIcon = burgerBtn.querySelector('.menu-icon');
            const closeIcon = burgerBtn.querySelector('.close-icon');
            if (menuIcon) menuIcon.classList.remove('hidden');
            if (closeIcon) closeIcon.classList.add('hidden');
        }

        burgerBtn.addEventListener('click', () => {
            if (menuSidebar.classList.contains('active')) {
                closeMenu();
            } else {
                openMenu();
            }
        });

        if (menuCloseBtn) menuCloseBtn.addEventListener('click', closeMenu);
        menuOverlay.addEventListener('click', closeMenu);

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeMenu();
        });

        menuItems.forEach(item => {
            item.addEventListener('click', () => {
                const view = item.getAttribute('data-view');
                switchView(view);
                closeMenu();
            });
        });
    }

    // Logout Modal
    const logoutBtn = document.getElementById('logoutBtn');
    const logoutModal = document.getElementById('logoutModal');
    const cancelLogoutBtn = document.getElementById('cancelLogoutBtn');
    const confirmLogoutBtn = document.getElementById('confirmLogoutBtn');

    if (logoutBtn && logoutModal) {
        logoutBtn.addEventListener('click', () => {
            logoutModal.classList.remove('hidden');
        });

        if (cancelLogoutBtn) {
            cancelLogoutBtn.addEventListener('click', () => {
                logoutModal.classList.add('hidden');
            });
        }

        if (confirmLogoutBtn) {
            confirmLogoutBtn.addEventListener('click', () => {
                window.location.href = '/login';
            });
        }

        logoutModal.addEventListener('click', (e) => {
            if (e.target === logoutModal) {
                logoutModal.classList.add('hidden');
            }
        });
    }

    // Initialize
    initChart();
    if (typeof lucide !== 'undefined') lucide.createIcons();
});

// ===== View Switching =====
function switchView(view) {
    activeView = view;
    
    document.querySelectorAll('.menu-item').forEach(item => {
        if (item.getAttribute('data-view') === view) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
    
    document.querySelectorAll('.view-container').forEach(container => {
        container.classList.remove('active');
    });
    
    const viewMap = {
        'dashboard': 'dashboardView',
        'cards': 'cardsView',
        'quiz': 'quizView'
    };
    
    const viewId = viewMap[view];
    if (viewId) {
        const viewEl = document.getElementById(viewId);
        if (viewEl) viewEl.classList.add('active');
    }
}

// ===== Chart =====
function initChart() {
    const ctx = document.getElementById('progressChart');
    if (!ctx) return;
    
    const data = [
        { day: 'Lun', cards: 28, time: 45 },
        { day: 'Mar', cards: 35, time: 52 },
        { day: 'Mer', cards: 42, time: 68 },
        { day: 'Jeu', cards: 38, time: 55 },
        { day: 'Ven', cards: 48, time: 72 },
        { day: 'Sam', cards: 55, time: 85 },
        { day: 'Dim', cards: 62, time: 92 },
    ];
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.day),
            datasets: [
                {
                    label: 'Cartes créées',
                    data: data.map(d => d.cards),
                    borderColor: '#ff6b35',
                    backgroundColor: 'rgba(255, 107, 53, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2,
                },
                {
                    label: 'Temps d\'apprentissage (min)',
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
                legend: { display: false },
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
                        font: { size: 12 }
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                        drawBorder: false,
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.3)',
                        font: { size: 12 }
                    }
                }
            }
        }
    });
}
