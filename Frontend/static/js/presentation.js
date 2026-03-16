// ===== Presentation Navigation =====
let currentSlide = 1;
const slides = document.querySelectorAll('.slide');
const totalSlides = slides.length;

// Elements
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const currentSlideEl = document.getElementById('currentSlide');
const totalSlidesEl = document.getElementById('totalSlides');
const progressFill = document.getElementById('progressFill');

// Initialize
function init() {
    totalSlidesEl.textContent = totalSlides;
    updateSlide();
}

// Update slide display
function updateSlide() {
    // Remove active class from all slides
    slides.forEach((slide, index) => {
        slide.classList.remove('active', 'prev');
        if (index < currentSlide - 1) {
            slide.classList.add('prev');
        }
    });
    
    // Add active class to current slide
    slides[currentSlide - 1].classList.add('active');
    
    // Update UI
    currentSlideEl.textContent = currentSlide;
    
    // Update progress bar
    const progress = (currentSlide / totalSlides) * 100;
    progressFill.style.width = `${progress}%`;
    
    // Update buttons state
    prevBtn.disabled = currentSlide === 1;
    nextBtn.disabled = currentSlide === totalSlides;
    
    // Reinitialize icons for the new slide
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

// Navigate to specific slide
function goToSlide(slideNumber) {
    if (slideNumber >= 1 && slideNumber <= totalSlides) {
        currentSlide = slideNumber;
        updateSlide();
    }
}

// Navigate to next slide
function nextSlide() {
    if (currentSlide < totalSlides) {
        currentSlide++;
        updateSlide();
    }
}

// Navigate to previous slide
function prevSlide() {
    if (currentSlide > 1) {
        currentSlide--;
        updateSlide();
    }
}

// Event listeners
prevBtn.addEventListener('click', prevSlide);
nextBtn.addEventListener('click', nextSlide);

// Keyboard navigation
document.addEventListener('keydown', (e) => {
    switch(e.key) {
        case 'ArrowRight':
        case ' ':
        case 'PageDown':
            e.preventDefault();
            nextSlide();
            break;
        case 'ArrowLeft':
        case 'PageUp':
            e.preventDefault();
            prevSlide();
            break;
        case 'Home':
            e.preventDefault();
            goToSlide(1);
            break;
        case 'End':
            e.preventDefault();
            goToSlide(totalSlides);
            break;
        case 'Escape':
            toggleFullscreen();
            break;
    }
});

// Touch/Swipe support for mobile
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
});

document.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
});

function handleSwipe() {
    const swipeThreshold = 50;
    const diff = touchStartX - touchEndX;
    
    if (Math.abs(diff) > swipeThreshold) {
        if (diff > 0) {
            // Swipe left - next slide
            nextSlide();
        } else {
            // Swipe right - previous slide
            prevSlide();
        }
    }
}

// Mouse wheel navigation (optional)
let isScrolling = false;
document.addEventListener('wheel', (e) => {
    if (isScrolling) return;
    
    isScrolling = true;
    setTimeout(() => {
        isScrolling = false;
    }, 500);
    
    if (e.deltaY > 0) {
        nextSlide();
    } else if (e.deltaY < 0) {
        prevSlide();
    }
}, { passive: true });

// Click navigation on slide edges
document.addEventListener('click', (e) => {
    const windowWidth = window.innerWidth;
    const clickX = e.clientX;
    const edgeThreshold = 100;
    
    // Don't interfere with control buttons or links
    if (e.target.closest('.controls') || 
        e.target.closest('a') || 
        e.target.closest('button')) {
        return;
    }
    
    if (clickX < edgeThreshold) {
        prevSlide();
    } else if (clickX > windowWidth - edgeThreshold) {
        nextSlide();
    }
});

// Fullscreen toggle
function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(err => {
            console.log('Error attempting to enable fullscreen:', err);
        });
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        }
    }
}

// Double-click to toggle fullscreen
document.addEventListener('dblclick', (e) => {
    if (!e.target.closest('.controls') && 
        !e.target.closest('a') && 
        !e.target.closest('button')) {
        toggleFullscreen();
    }
});

// Slide number display on hover (optional enhancement)
slides.forEach((slide, index) => {
    slide.addEventListener('mouseenter', () => {
        const slideNumber = slide.querySelector('.slide-number');
        if (slideNumber) {
            slideNumber.style.opacity = '0.2';
        }
    });
    
    slide.addEventListener('mouseleave', () => {
        const slideNumber = slide.querySelector('.slide-number');
        if (slideNumber) {
            slideNumber.style.opacity = '0.1';
        }
    });
});

// Presenter notes (press 'P' to toggle)
let notesVisible = false;
document.addEventListener('keydown', (e) => {
    if (e.key === 'p' || e.key === 'P') {
        notesVisible = !notesVisible;
        console.log(`Presenter notes ${notesVisible ? 'shown' : 'hidden'}`);
        // You can implement a notes panel here
    }
});

// Timer (press 'T' to start/reset)
let timerStarted = false;
let startTime = null;
let timerInterval = null;

function startTimer() {
    startTime = Date.now();
    timerInterval = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const minutes = Math.floor(elapsed / 60000);
        const seconds = Math.floor((elapsed % 60000) / 1000);
        console.log(`Timer: ${minutes}:${seconds.toString().padStart(2, '0')}`);
    }, 1000);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

document.addEventListener('keydown', (e) => {
    if (e.key === 't' || e.key === 'T') {
        if (!timerStarted) {
            startTimer();
            timerStarted = true;
            console.log('Timer started');
        } else {
            stopTimer();
            timerStarted = false;
            console.log('Timer stopped');
        }
    }
});

// Print mode (press Ctrl/Cmd + P)
window.addEventListener('beforeprint', () => {
    // Show all slides for printing
    slides.forEach(slide => {
        slide.style.position = 'relative';
        slide.style.opacity = '1';
        slide.style.visibility = 'visible';
        slide.style.transform = 'none';
        slide.style.pageBreakAfter = 'always';
    });
});

window.addEventListener('afterprint', () => {
    // Restore slide navigation after printing
    updateSlide();
});

// Auto-advance demo (press 'A' to toggle)
let autoAdvance = false;
let autoInterval = null;

function toggleAutoAdvance() {
    autoAdvance = !autoAdvance;
    
    if (autoAdvance) {
        console.log('Auto-advance enabled (every 10 seconds)');
        autoInterval = setInterval(() => {
            if (currentSlide < totalSlides) {
                nextSlide();
            } else {
                // Loop back to start
                goToSlide(1);
            }
        }, 10000); // 10 seconds per slide
    } else {
        console.log('Auto-advance disabled');
        if (autoInterval) {
            clearInterval(autoInterval);
            autoInterval = null;
        }
    }
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'a' || e.key === 'A') {
        toggleAutoAdvance();
    }
});

// Video placeholder click handler
const videoPlaceholder = document.querySelector('.video-placeholder');
if (videoPlaceholder) {
    videoPlaceholder.addEventListener('click', () => {
        alert('This is where your demo video would play.\n\nTo add a real video:\n1. Upload your video to /static/videos/demo.mp4\n2. Uncomment the <video> tag in presentation.html');
    });
}

// Overview mode (press 'O' to toggle)
let overviewMode = false;

function toggleOverview() {
    overviewMode = !overviewMode;
    const container = document.querySelector('.slides-container');
    
    if (overviewMode) {
        container.style.display = 'grid';
        container.style.gridTemplateColumns = 'repeat(auto-fit, minmax(300px, 1fr))';
        container.style.gap = '2rem';
        container.style.padding = '2rem';
        container.style.overflowY = 'auto';
        container.style.height = '100vh';
        
        slides.forEach((slide, index) => {
            slide.style.position = 'relative';
            slide.style.opacity = '1';
            slide.style.visibility = 'visible';
            slide.style.transform = 'scale(0.3)';
            slide.style.transformOrigin = 'top left';
            slide.style.width = '300%';
            slide.style.height = '300%';
            slide.style.cursor = 'pointer';
            
            // Add click handler to go to slide
            slide.addEventListener('click', () => {
                toggleOverview();
                goToSlide(index + 1);
            });
        });
        
        // Hide controls in overview
        document.querySelector('.controls').style.display = 'none';
    } else {
        container.style.display = '';
        container.style.gridTemplateColumns = '';
        container.style.gap = '';
        container.style.padding = '';
        container.style.overflowY = '';
        container.style.height = '';
        
        updateSlide();
        
        // Show controls
        document.querySelector('.controls').style.display = 'flex';
    }
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'o' || e.key === 'O') {
        toggleOverview();
    }
});

// Help overlay (press 'H' or '?')
function showHelp() {
    const helpText = `
KEYBOARD SHORTCUTS:

Navigation:
  →, Space, PageDown - Next slide
  ←, PageUp - Previous slide
  Home - First slide
  End - Last slide

Presentation:
  F, Esc - Toggle fullscreen
  O - Overview mode
  A - Auto-advance
  T - Start/stop timer
  P - Presenter notes
  H, ? - Show this help

Other:
  Double-click - Toggle fullscreen
  Ctrl/Cmd + P - Print slides
  Swipe left/right - Navigate (mobile)
    `;
    
    alert(helpText);
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'h' || e.key === 'H' || e.key === '?') {
        showHelp();
    }
    
    if (e.key === 'f' || e.key === 'F') {
        toggleFullscreen();
    }
});

// Initialize presentation
init();

// Log keyboard shortcuts on load
console.log('%c SmartCards Presentation Loaded ', 'background: linear-gradient(to right, #ff6b35, #9b59b6); color: white; font-size: 16px; padding: 10px;');
console.log('Press H or ? for keyboard shortcuts');
