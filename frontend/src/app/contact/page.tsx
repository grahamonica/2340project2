'use client';

import { useState } from 'react';

export default function ContactPage() {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        message: ''
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        // TODO: Implement your contact form submission logic here
        console.log('Form submitted:', formData);
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4">
            <div className="max-w-md w-full bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg">
                <h1 className="text-2xl font-bold text-yellow-400 mb-4">Contact the Developers</h1>
                <p className="text-gray-600 dark:text-gray-300 mb-6">
                    If you have any questions, suggestions, or feedback, feel free to reach out to us. We'd love to hear from you!
                </p>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <input
                        type="text"
                        placeholder="Your Name"
                        className="w-full p-3 rounded-lg bg-gray-100 dark:bg-gray-700 border border-yellow-400"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        required
                    />
                    <input
                        type="email"
                        placeholder="Your Email"
                        className="w-full p-3 rounded-lg bg-gray-100 dark:bg-gray-700 border border-yellow-400"
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        required
                    />
                    <textarea
                        placeholder="Your Message"
                        rows={5}
                        className="w-full p-3 rounded-lg bg-gray-100 dark:bg-gray-700 border border-yellow-400"
                        value={formData.message}
                        onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                        required
                    />
                    <button
                        type="submit"
                        className="w-full bg-yellow-400 text-black font-bold py-3 px-4 rounded-lg hover:bg-yellow-500 transition-colors"
                    >
                        Send Message
                    </button>
                </form>
            </div>
        </div>
    );
}