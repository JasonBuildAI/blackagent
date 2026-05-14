/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'risk-critical': '#dc2626',
        'risk-high': '#ea580c',
        'risk-medium': '#ca8a04',
        'risk-low': '#16a34a',
        'primary-accent': '#06b6d4',
        'bg-dark': '#0f172a',
        'card-bg': '#1e293b',
        'card-border': '#334155',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
};