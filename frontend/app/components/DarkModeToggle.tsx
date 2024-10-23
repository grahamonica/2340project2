"use client";

import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';

const DarkModeToggle = () => {
    const [mounted, setMounted] = useState(false);
    const { theme, setTheme } = useTheme();

    useEffect(() => {
        setMounted(true);
    }, []);

    if (!mounted) {
        return null;
    }

    return (
        <button
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            className="p-2 rounded-md bg-gray-200 dark:bg-gray-800"
        >
            {theme === 'dark' ? '🌞' : '🌙'}
        </button>
    );
};

export default DarkModeToggle;