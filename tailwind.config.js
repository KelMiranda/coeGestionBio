/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html', // Archivos HTML en la carpeta templates
    './static/**/*.js',      // Si tienes archivos JavaScript donde usas clases de Tailwind
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

