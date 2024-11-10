'use client'

import { useTheme } from 'next-themes'

export function ThemeToggle() {
    const { theme, setTheme } = useTheme()

    return (
        <button
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            className="p-2 rounded-full hover:bg-yellow-400 hover:text-black transition-colors"
        >
            {theme === 'dark' ? '🌞' : '🌙'}
        </button>
    )
}