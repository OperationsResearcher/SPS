/* Derlenmiş Tailwind yapılandırması (TASK-236 — CSP: unsafe-eval kaldırma).
   Play CDN'deki inline config (ui/static/platform/js/tailwind.config.js) ile
   birebir aynı theme; content taraması template + JS'i kapsar.
   Derleme: scripts/frontend/build_css.ps1  */
module.exports = {
  darkMode: 'class',
  content: [
    '../../ui/templates/**/*.html',
    '../../ui/static/platform/js/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        brand: { DEFAULT: '#4F46E5', light: '#818CF8', dark: '#3730A3' }
      }
    }
  }
};
