(function () {
    'use strict';

    const UI = {
        toast(message, type = 'success') {
            const container = document.getElementById('app-toast-container');
            if (!container || !window.bootstrap) return;

            const iconMap = {
                success: 'bi-check-circle-fill',
                danger: 'bi-exclamation-octagon-fill',
                warning: 'bi-exclamation-triangle-fill',
                info: 'bi-info-circle-fill'
            };
            const toast = document.createElement('div');
            toast.className = 'toast app-toast';
            toast.setAttribute('role', 'status');
            toast.setAttribute('aria-live', 'polite');
            toast.innerHTML = `
                <div class="toast-body">
                    <i class="bi ${iconMap[type] || iconMap.info}"></i>
                    <div class="flex-grow-1">${escapeHtml(message)}</div>
                    <button type="button" class="btn-close ms-2" data-bs-dismiss="toast" aria-label="Cerrar"></button>
                </div>`;
            container.appendChild(toast);
            const instance = new bootstrap.Toast(toast, { delay: 3200 });
            toast.addEventListener('hidden.bs.toast', () => toast.remove());
            instance.show();
        }
    };

    function escapeHtml(value) {
        return String(value ?? '')
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;')
            .replaceAll("'", '&#039;');
    }

    function enhanceForms() {
        document.querySelectorAll('form input:not([type="checkbox"]):not([type="radio"]):not([type="hidden"]):not([type="submit"]), form textarea').forEach((el) => {
            if (!el.classList.contains('form-control')) el.classList.add('form-control');
        });
        document.querySelectorAll('form select').forEach((el) => {
            if (!el.classList.contains('form-select')) el.classList.add('form-select');
        });
        document.querySelectorAll('form input[type="checkbox"]').forEach((el) => {
            if (!el.classList.contains('form-check-input')) el.classList.add('form-check-input');
        });
    }

    function initReveal() {
        const elements = document.querySelectorAll('.reveal');
        if (!elements.length) return;
        if (!('IntersectionObserver' in window) || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            elements.forEach((el) => el.classList.add('is-visible'));
            return;
        }
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: .08, rootMargin: '0px 0px -30px 0px' });
        elements.forEach((el) => observer.observe(el));
    }

    function initNavbar() {
        const navbar = document.querySelector('.app-navbar');
        if (!navbar) return;
        const sync = () => navbar.classList.toggle('is-scrolled', window.scrollY > 8);
        sync();
        window.addEventListener('scroll', sync, { passive: true });
    }

    function initSearchShortcut() {
        const input = document.getElementById('navbar-catalog-search');
        if (!input) return;
        document.addEventListener('keydown', (event) => {
            if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
                event.preventDefault();
                input.focus();
                input.select();
            }
        });
    }

    function initTooltips() {
        if (!window.bootstrap) return;
        document.querySelectorAll('[title]').forEach((el) => {
            if (el.closest('.ui-autocomplete')) return;
            try { new bootstrap.Tooltip(el, { trigger: 'hover' }); } catch (_) { /* noop */ }
        });
    }

    window.PatitasUI = UI;
    window.PatitasEscapeHtml = escapeHtml;

    document.addEventListener('DOMContentLoaded', () => {
        enhanceForms();
        initReveal();
        initNavbar();
        initSearchShortcut();
        initTooltips();
    });
})();
