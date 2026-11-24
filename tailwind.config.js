/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        baloo: ['"Baloo Bhaijaan 2"', 'system-ui', 'sans-serif'],
        alex: ['Alexandria', 'system-ui', 'sans-serif'],
      },
      colors: {
        grape: { DEFAULT: '#6F52FF', deep: '#4B34D1', night: '#2E2290', soft: '#9B7BFF' },
        sun: '#FFD83D',
        tang: '#FF6B3D',
        mint: '#5BD38B',
        bubble: '#FF8DB7',
        sky: '#3D8BFF',
      },
    },
  },
  plugins: [],
}
