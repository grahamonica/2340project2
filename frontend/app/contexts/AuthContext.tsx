"use client";

import { jwtDecode } from 'jwt-decode';
import React, { createContext, useContext, useEffect, useState } from 'react';
import { API_URL } from '../utils/api';

interface AuthContextType {
    user: any;
    login: (tokens: { access: string, refresh: string }) => void;
    logout: () => Promise<void>;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface JwtPayload {
    user_id: number;
    username: string;
    exp: number;
    [key: string]: any; // This allows for any additional fields in the token
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<any>(null);

    const checkAndSetUser = (token: string | null) => {
        if (token) {
            try {
                const decodedToken = jwtDecode<JwtPayload>(token);
                console.log('Decoded token:', decodedToken);  // Add this line for debugging
                if (decodedToken.exp * 1000 > Date.now()) {
                    setUser({
                        id: decodedToken.user_id,
                        username: decodedToken.username,
                    });
                } else {
                    localStorage.removeItem('accessToken');
                    localStorage.removeItem('refreshToken');
                    setUser(null);
                }
            } catch (error) {
                console.error('Invalid token:', error);
                localStorage.removeItem('accessToken');
                localStorage.removeItem('refreshToken');
                setUser(null);
            }
        } else {
            setUser(null);
        }
    };

    useEffect(() => {
        const token = localStorage.getItem('accessToken');
        checkAndSetUser(token);

        const handleStorageChange = (e: StorageEvent) => {
            if (e.key === 'accessToken') {
                checkAndSetUser(e.newValue);
            }
        };

        window.addEventListener('storage', handleStorageChange);
        return () => window.removeEventListener('storage', handleStorageChange);
    }, []);

    const login = (tokens: { access: string, refresh: string }) => {
        console.log('Received tokens:', tokens);
        localStorage.setItem('accessToken', tokens.access);
        localStorage.setItem('refreshToken', tokens.refresh);
        checkAndSetUser(tokens.access);
    };

    const getHeaders = () => {
        const token = localStorage.getItem('accessToken');
        return {
            'Authorization': token ? `Bearer ${token}` : '',
        };
    };

    const logout = async () => {
        try {
            const refreshToken = localStorage.getItem('refreshToken');
            const response = await fetch(`${API_URL}/logout/`, {
                method: "POST",
                headers: {
                    ...getHeaders(),
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ refresh: refreshToken }),
            });

            if (!response.ok) {
                throw new Error("Logout failed");
            }

            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            setUser(null);

            return response.json();
        } catch (error) {
            console.error('Logout error:', error);
            throw error;
        }
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};