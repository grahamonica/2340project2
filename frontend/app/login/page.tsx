"use client";

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import AuthPage from '../components/AuthPage';
import { useAuth } from '../contexts/AuthContext';

export default function LoginPage() {
    const { isAuthenticated } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (isAuthenticated) {
            router.push('/');
        }
    }, [isAuthenticated, router]);

    return <AuthPage />;
}