/**
 * Gmail Unsubscribe - Theme Module (light / dark)
 * The initial theme is applied by an inline script in <head> to avoid a flash.
 */

window.GmailCleaner = window.GmailCleaner || {};

GmailCleaner.Theme = {
    storageKey: 'gmail-cleaner-theme',

    current() {
        return document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
    },

    apply(theme) {
        if (theme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
        } else {
            document.documentElement.removeAttribute('data-theme');
        }
        const btn = document.getElementById('themeToggle');
        if (btn) {
            const label = theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
            btn.title = label;
            btn.setAttribute('aria-label', label);
        }
    },

    toggle() {
        const next = this.current() === 'dark' ? 'light' : 'dark';
        this.apply(next);
        try {
            localStorage.setItem(this.storageKey, next);
        } catch (e) {
            // Storage unavailable (private mode) - theme just won't persist
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    GmailCleaner.Theme.apply(GmailCleaner.Theme.current());
});
