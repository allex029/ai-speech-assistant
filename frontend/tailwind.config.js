/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        background: '#09090B',
        card: '#18181B',
        accent: '#3B82F6',
        accentSecondary: '#8B5CF6',
        text: '#F4F4F5',
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(59,130,246,0.2), 0 0 40px rgba(59,130,246,0.15)',
      },
    },
  },
  plugins: [],
};

