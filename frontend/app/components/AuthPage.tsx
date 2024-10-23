"use client";

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { checkUserExists, registerOrLogin } from '../utils/api';

export default function AuthPage() {
  const { login: authLogin } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const { exists } = await checkUserExists(username, email);
      const data = await registerOrLogin(username, password, email);

      console.log('Received data:', data);

      if (data.access && data.refresh) {
        authLogin({ access: data.access, refresh: data.refresh });
        router.push('/');
      } else {
        setError('Authentication failed. Please try again.');
      }
    } catch (error) {
      console.error('Authentication failed', error);
      setError('An error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center bg-cover bg-center relative"
      style={{ backgroundImage: 'url(/images/background.jpg)' }} // Path to your image
    >
      {/* Overlay for better contrast */}
      <div className="absolute inset-0 bg-black opacity-40 z-0"></div>

      <Link href="/" className="absolute top-4 left-4 bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 transition-colors z-10">
        Back to Home
      </Link>

      {/* Login Form Container */}
      <div className="relative z-10 bg-white bg-opacity-90 p-8 rounded-xl shadow-2xl max-w-md w-full border-4 border-blue-300 transform transition-all hover:scale-105">
        <h1 className="text-4xl font-bold mb-6 text-center text-gray-800">Login</h1>

        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full p-3 mb-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-400 focus:outline-none transition-shadow shadow-sm"
            required
          />
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full p-3 mb-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-400 focus:outline-none transition-shadow shadow-sm"
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full p-3 mb-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-400 focus:outline-none transition-shadow shadow-sm"
            required
          />
          <button
            type="submit"
            className="w-full py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors transform hover:scale-105 flex items-center justify-center"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </>
            ) : (
              'Login'
            )}
          </button>

          {error && <p className="text-red-500 mt-4 text-center">{error}</p>}
        </form>
      </div>
    </div>
  );
}