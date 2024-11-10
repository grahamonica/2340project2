'use client'

import { ThemeToggle } from '@/app/components/layout/ThemeToggle'
import Link from 'next/link'

export function Header() {
    return (
        <header className="w-full flex justify-between items-center p-4 bg-gray-800 shadow-yellow-400 shadow-sm sticky top-0">
            <h1 className="text-2xl font-bold text-yellow-400">Spotify Wrapped</h1>

            <div className="flex items-center gap-4">
                <Link
                    href="/contact"
                    className="px-4 py-2 rounded-full hover:bg-yellow-400 hover:text-black transition-colors"
                >
                    Contact the Developers
                </Link>
                <Link
                    href="/auth/logout"
                    className="px-4 py-2 rounded-full hover:bg-yellow-400 hover:text-black transition-colors"
                >
                    Logout
                </Link>
                <ThemeToggle />
            </div>
        </header>
    )
}