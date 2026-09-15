// Search Overlay
document.addEventListener('DOMContentLoaded', function() {
    const searchBtn = document.querySelector('.search-trigger');
    const searchOverlay = document.querySelector('.search-overlay');
    const closeSearchBtn = document.querySelector('.close-search');
    const searchInput = document.querySelector('.search-overlay input[type="search"]');

    if (searchBtn && searchOverlay) {
        searchBtn.addEventListener('click', function(e) {
            e.preventDefault();
            searchOverlay.classList.add('active');
            setTimeout(() => {
                searchInput.focus();
            }, 300);
        });

        closeSearchBtn.addEventListener('click', function() {
            searchOverlay.classList.remove('active');
        });

        // Close on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && searchOverlay.classList.contains('active')) {
                searchOverlay.classList.remove('active');
            }
        });
    }
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Initialize tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
});

// Dark mode toggle
document.addEventListener('DOMContentLoaded', function () {
    const toggleBtn = document.getElementById('theme-toggle');
    const toggleIcon = document.getElementById('theme-toggle-icon');
    if (!toggleBtn || !toggleIcon) return;

    function syncIcon() {
        const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
        toggleIcon.className = isDark ? 'bi bi-sun' : 'bi bi-moon-stars';
        toggleBtn.setAttribute('aria-pressed', isDark ? 'true' : 'false');
    }

    syncIcon();

    toggleBtn.addEventListener('click', function () {
        const current = document.documentElement.getAttribute('data-bs-theme') === 'dark' ? 'dark' : 'light';
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-bs-theme', next);
        localStorage.setItem('theme', next);
        syncIcon();
    });
});

// Newsletter signup: submit via fetch so feedback shows right at the
// form instead of a full page reload/redirect (which, combined with
// Django's messages framework, was showing "Please correct the errors
// below" on whatever page the visitor navigated to next - not
// necessarily the page they submitted from).
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('newsletterForm');
    const feedback = document.getElementById('newsletterFeedback');
    if (!form || !feedback) return;

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        feedback.textContent = '';
        feedback.classList.remove('text-danger', 'text-success');

        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.disabled = true;

        fetch(form.action, {
            method: 'POST',
            body: new FormData(form),
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
        })
            .then(function (r) { return r.json().then(function (data) { return { ok: r.ok, data: data }; }); })
            .then(function (result) {
                const isSuccess = result.data.status === 'success';
                feedback.textContent = result.data.message;
                feedback.classList.add(isSuccess ? 'text-success' : 'text-danger');
                if (isSuccess) {
                    form.reset();
                }
            })
            .catch(function () {
                feedback.textContent = 'Something went wrong - please try again.';
                feedback.classList.add('text-danger');
            })
            .finally(function () {
                submitBtn.disabled = false;
            });
    });
});