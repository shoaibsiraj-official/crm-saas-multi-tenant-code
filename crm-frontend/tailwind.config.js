/** @type {import('tailwindcss').Config} */
module.exports = {
darkMode: false, // dark mode disabled
content: ["./src/**/*.{js,jsx,ts,tsx}"],
theme: {
extend: {
colors: {
primary: {
50: '#f0f9ff',
100: '#e0f2fe',
500: '#0ea5e9',
600: '#0284c7',
700: '#0369a1',
},
},
boxShadow: {
soft: '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)',
glass: '0 8px 32px 0 rgba(31, 38, 135, 0.15)',
},
animation: {
gradient: 'gradient 15s ease infinite',
float: 'float 6s ease-in-out infinite',
},
keyframes: {
gradient: {
'0%, 100%': { backgroundPosition: '0% 50%' },
'50%': { backgroundPosition: '100% 50%' },
},
float: {
'0%, 100%': { transform: 'translateY(0)' },
'50%': { transform: 'translateY(-20px)' },
},
},
},
},
plugins: [],
}
