"use client";

import { useAuth } from '../contexts/AuthContext';
import { useEffect, useState } from 'react';
import { fetchFavorites, toggleFavorite, fetchUserReviews, removeReview } from '../utils/api';
import { Restaurant, Review } from '../utils/schema';
import Link from 'next/link';
import DarkModeToggle from '../components/DarkModeToggle';
import RestaurantModal from '../components/RestaurantModal';

export default function ProfilePage() {
    const { user } = useAuth();
    const [favorites, setFavorites] = useState<Restaurant[]>([]);
    const [userReviews, setUserReviews] = useState<Review[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [selectedRestaurant, setSelectedRestaurant] = useState<Restaurant | null>(null);

    useEffect(() => {
        if (user) {
            loadFavorites();
            loadUserReviews();
        }
    }, [user]);

    const loadFavorites = async () => {
        try {
            setIsLoading(true);
            const favoritesData = await fetchFavorites();
            setFavorites(favoritesData);
        } catch (error) {
            setError('Failed to fetch favorites. Please try again later.');
            console.error('Error fetching favorites:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const loadUserReviews = async () => {
        try {
            const reviewsData = await fetchUserReviews();
            setUserReviews(reviewsData);
        } catch (error) {
            console.error('Error fetching user reviews:', error);
        }
    };

    const handleToggleFavorite = async (restaurantId: string) => {
        try {
            await toggleFavorite(restaurantId);
            setFavorites(favorites.filter(fav => fav.id !== restaurantId));
            if (selectedRestaurant && selectedRestaurant.id === restaurantId) {
                setSelectedRestaurant(null);
            }
        } catch (error) {
            console.error('Error removing favorite:', error);
        }
    };

    const handleViewDetails = (restaurant: Restaurant) => {
        setSelectedRestaurant(restaurant);
    };

    const handleCloseModal = () => {
        setSelectedRestaurant(null);
    };

    const handleRemoveReview = async (reviewId: number) => {
        try {
            await removeReview(reviewId);
            setUserReviews(userReviews.filter(review => review.id !== reviewId));
        } catch (error) {
            console.error('Error removing review:', error);
            alert('Failed to remove review. Please try again.');
        }
    };

    return (
        <div className="min-h-screen bg-background text-foreground">
            <header className="bg-card-background text-card-foreground p-4 shadow-md">
                <div className="container mx-auto flex justify-between items-center">
                    <h1 className="text-2xl font-bold">🍽 Restaurant Finder</h1>
                    <nav className="flex items-center space-x-4">
                        <Link href="/" className="hover:underline">Home</Link>
                        <Link href="/profile" className="font-semibold">Profile</Link>
                        <DarkModeToggle />
                    </nav>
                </div>
            </header>

            <main className="container mx-auto px-4 py-8">
                {user ? (
                    <div>
                        {/* <h1 className="text-3xl font-semibold mb-8">Welcome to Your Profile, {user.username}!</h1> */}
                        <h2 className="text-2xl font-semibold mb-4">Your Favorite Restaurants</h2>
                        {isLoading ? (
                            <div className="flex justify-center items-center">
                                <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-500"></div>
                            </div>
                        ) : error ? (
                            <p className="text-red-500 text-center">{error}</p>
                        ) : favorites.length === 0 ? (
                            <p className="text-center text-gray-600 dark:text-gray-400">No favorites added yet.</p>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                                {favorites.map((restaurant) => (
                                    <div key={restaurant.id} className="bg-card-background text-card-foreground rounded-lg shadow-md overflow-hidden transition-transform hover:scale-105">
                                        <div className="p-6">
                                            <h2 className="text-xl font-bold mb-2">{restaurant.name}</h2>
                                            <p className="text-gray-600 dark:text-gray-400 mb-4">{restaurant.address}</p>
                                            <div className="flex items-center mb-4">
                                                {[...Array(5)].map((_, i) => (
                                                    <svg key={i} className={`w-5 h-5 ${i < Math.floor(restaurant.rating || 0) ? 'text-yellow-400' : 'text-gray-300 dark:text-gray-600'} fill-current`} viewBox="0 0 20 20">
                                                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                                    </svg>
                                                ))}
                                                <span className="ml-2 text-gray-600 dark:text-gray-400">{restaurant.rating?.toFixed(1)}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <button
                                                    onClick={() => handleViewDetails(restaurant)}
                                                    className="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
                                                >
                                                    View Details
                                                </button>
                                                <button
                                                    onClick={() => handleToggleFavorite(restaurant.id)}
                                                    className="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-400 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-50"
                                                >
                                                    Remove from Favorites
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}

                        <h2 className="text-2xl font-semibold mb-4 mt-8 ml-2">Your Reviews</h2>
                        {userReviews.length === 0 ? (
                            <p className="text-center text-gray-600 dark:text-gray-400">No reviews added yet.</p>
                        ) : (
                            <div className="space-y-4">
                                {userReviews.map((review) => (
                                    <div key={review.id} className="bg-card-background text-card-foreground p-4 rounded-lg shadow">
                                        <div className="flex justify-between items-start mb-2">
                                            <h3 className="text-xl font-semibold">{review.title}</h3>
                                            <button
                                                onClick={() => handleRemoveReview(review.id)}
                                                className="bg-blue-500 text-white py-1 px-2 rounded text-sm hover:bg-blue-600 transition-colors"
                                            >
                                                Remove
                                            </button>
                                        </div>
                                        <p className="mb-2">Rating: {review.rating}/5</p>
                                        <p>{review.content}</p>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                ) : (
                    <p className="text-center text-gray-600 dark:text-gray-400">Please log in to view your profile.</p>
                )}
            </main>

            {selectedRestaurant && (
                <RestaurantModal
                    restaurant={selectedRestaurant}
                    onClose={handleCloseModal}
                    onToggleFavorite={handleToggleFavorite}
                    isFromFavorites={true}
                />
            )}
        </div>
    );
}