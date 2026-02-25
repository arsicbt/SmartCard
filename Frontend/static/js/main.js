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
