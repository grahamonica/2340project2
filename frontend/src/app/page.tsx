'use client';

import Link from 'next/link';
import { useState } from 'react';

export default function LoginPage() {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="login-box">
        <h1 className="text-2xl font-bold text-[#FFD700] mb-2">
          Welcome to Spotify Wrapped!
        </h1>
        <p className="text-[#333333] dark:text-gray-300 text-base mb-6">
          Your Year, Your Data. Log in to explore your personalized insights!
        </p>

        <form className="space-y-4">
          <input
            type="text"
            placeholder="Username"
            className="form-input"
            value={formData.username}
            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
          />
          <input
            type="password"
            placeholder="Password"
            className="form-input"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          />
          <button type="submit" className="btn-primary">
            Log In
          </button>
        </form>

        <p className="mt-4 text-sm text-[#333333] dark:text-gray-400">
          Don't have an account?{' '}
          <Link href="/signup" className="text-[#FFD700] hover:underline font-bold">
            Sign up here
          </Link>
        </p>
      </div>
    </div>
  );
}