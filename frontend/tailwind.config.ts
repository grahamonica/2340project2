import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        spotify: {
          gold: '#FFD700',
          goldHover: '#FFC700',
          dark: '#1E1E1E',
          darkSecondary: '#333333',
          darkInput: '#444444',
        },
      },
    },
  },
  plugins: [],
}

export default config