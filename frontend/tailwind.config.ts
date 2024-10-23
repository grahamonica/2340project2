import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: 'class', // Enable class-based dark mode toggling
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Use custom CSS variables for background and foreground that can adapt in light and dark mode
        background: "var(--background)",
        foreground: "var(--foreground)",
      },
      
    },
  },
  plugins: [],
};



export default config;
