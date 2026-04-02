/* Tailwind CDN konfigürasyonu — base.html'den önce yüklenir */
tailwind.config = {
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                brand: { DEFAULT: '#4F46E5', light: '#818CF8', dark: '#3730A3' }
            }
        }
    }
};
