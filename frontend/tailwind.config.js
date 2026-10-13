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
          950: '#F3F5F1',
          900: '#EDF2ED',
          850: '#FFFEFA',
          800: '#DCE5DF',
          700: '#C9D8D0',
        },
        slate: {
          100: '#263E40',
          200: '#344C4E',
          300: '#485F60',
          400: '#617475',
          500: '#718383',
          600: '#849392',
          700: '#A6B5AE',
          800: '#D2DDD6',
          900: '#EDF2ED',
        },
        cyan: {
          50: '#F2F8F5', 100: '#E4F1EA', 200: '#CFE4D9', 300: '#3E7C72',
          400: '#286B62', 500: '#28675E', 600: '#20584F', 700: '#184D48',
          800: '#173E39', 900: '#E8F1EC', 950: '#E8F1EC',
        },
        blue: {
          50: '#F3F7F9', 100: '#E8F0F4', 200: '#D7E5EC', 300: '#456C8A',
          400: '#3B6887', 500: '#386C8A', 600: '#315F7E', 700: '#274F69',
          800: '#1F4056', 900: '#173448', 950: '#EAF0F4',
        },
        emerald: {
          50: '#F1F8F4', 100: '#E6F2EA', 200: '#D4E8DA', 300: '#337D61',
          400: '#369B70', 500: '#2F8A69', 600: '#257653', 700: '#1E6046',
          800: '#194C39', 900: '#143B2E', 950: '#E7F0EB',
        },
        amber: {
          50: '#FBF8EF', 100: '#F7F0DD', 200: '#80612D', 300: '#846737',
          400: '#987B48', 500: '#A67B36', 600: '#8D662D', 700: '#705124',
          800: '#543D1D', 900: '#3A2C1A', 950: '#F6EFDF',
        },
        red: {
          50: '#FDF7F5', 100: '#F9ECE8', 200: '#984D42', 300: '#984D42',
          400: '#A75447', 500: '#A0483D', 600: '#873A33', 700: '#6F302B',
          800: '#532723', 900: '#39201C', 950: '#F8EBE7',
        },
        brand: {
          blue: '#315F7E',
          blueHover: '#274F69',
          cyan: '#28675E',
          cyanLight: '#60998C',
        },
        surface: '#FFFEFA',
        page: '#F3F5F1',
        subtle: '#EDF2ED',
        'border-light': '#DCE5DF',
        'border-subtle': '#E7ECE7',
        'navy-primary': '#173A3B',
        'navy-secondary': '#24524F',
        'ink-main': '#1C3437',
        'ink-secondary': '#53686A',
        'teal-muted': '#28675E',
        'teal-light': '#E8F1EC',
        'teal-border': '#C9DED4',
        'danger-bg': '#F9ECE8',
        'danger-border': '#E9C9C2',
        'danger-text': '#8C4038',
      },
      fontFamily: {
        sans: ['Aptos', 'Segoe UI Variable', 'Segoe UI', 'sans-serif'],
        display: ['Georgia', 'Times New Roman', 'serif'],
      },
      boxShadow: {
        card: '0 8px 24px rgba(27, 54, 47, 0.06)',
      },
    },
  },
  plugins: [],
}
