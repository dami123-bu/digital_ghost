/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        'dg-navy':     '#0F1B2D',
        'dg-blue':     '#1A2E4A',
        'dg-accent':   '#3B82F6',
        'dg-surface':  '#162033',
        'dg-border':   '#1E3050',
        'dg-text':     '#CBD5E1',
        'dg-muted':    '#64748B',
        'dg-clean':    '#10B981',
        'dg-poison':   '#EF4444',
        'dg-defend':   '#F59E0B',
        'dg-orange':   '#F97316',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['IBM Plex Mono', 'monospace'],
      },
      animation: {
        'fade-in':  'fadeIn 0.2s ease-out',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: { '0%': { opacity: '0', transform: 'translateY(4px)' }, '100%': { opacity: '1', transform: 'translateY(0)' } },
      },
    },
  },
  plugins: [],
  safelist: [
    { pattern: /border-(dg-clean|dg-poison|dg-defend)/ },
    { pattern: /bg-(dg-clean|dg-poison|dg-defend)/ },
    { pattern: /text-(dg-clean|dg-poison|dg-defend)/ },
  ],
}
