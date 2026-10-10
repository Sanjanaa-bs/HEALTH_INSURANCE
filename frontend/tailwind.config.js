/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#070D1E', // deepest navy canvas
          900: '#0C162E', // primary page background
          850: '#111F3F', // card / content surface
          800: '#172B54', // border / hover surface
          700: '#223C72', // accent border
        },
        brand: {
          blue: '#2563EB',
          blueHover: '#1D4ED8',
          cyan: '#0EA5E9',
          cyanLight: '#38BDF8',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
