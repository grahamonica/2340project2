'use client';

import Link from 'next/link';
import { useState } from 'react';

export default function SignUpPage() {
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        confirmPassword: ''
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        // TODO: Implement your signup logic here
        console.log('Signup form submitted:', formData);
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4">
            <div className="max-w-md w-full bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg">
                <h1 className="text-2xl font-bold text-yellow-400 mb-2">Join Spotify Wrapped</h1>
                <p className="text-gray-600 dark:text-gray-300 mb-6">
                    Create your account to see your personalized wrap-up experience!
                </p>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <input
                        type="text"
                        placeholder="Username"
                        className="w-full p-3 rounded-lg bg-gray-100 dark:bg-gray-700 border border-yellow-400"
                        value={formData.username}
                        onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                        required
                    />
                    <input
                        type="password"
                        placeholder="Password"
                        className="w-full p-3 rounded-lg bg-gray-100 dark:bg-gray-700 border border-yellow-400"
                        value={formData.password}
                        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                        required
                    />
                    <input
                        type="password"
                        placeholder="Confirm Password"
                        className="w-full p-3 rounded-lg bg-gray-100 dark:bg-gray-700 border border-yellow-400"
                        value={formData.confirmPassword}
                        onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                        required
                    />
                    <button
                        type="submit"
                        className="w-full bg-yellow-400 text-black font-bold py-3 px-4 rounded-lg hover:bg-yellow-500 transition-colors"
                    >
                        Sign Up
                    </button>
                </form>

                <p className="mt-4 text-sm text-gray-600 dark:text-gray-400">
                    Already have an account?{' '}
                    <Link href="/login" className="text-yellow-400 hover:underline font-bold">
                        Log in here
                    </Link>
                </p>

                <div className="mt-8 text-xs text-gray-500 dark:text-gray-400 text-center">
                    © 2024 Spotify Wrapped. All rights reserved.
                </div>
            </div>
        </div>
    );
}