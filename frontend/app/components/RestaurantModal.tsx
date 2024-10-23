import React, { useState } from 'react';
import { addReview } from '../utils/api';
import { Restaurant, Review } from '../utils/schema';

interface RestaurantModalProps {
    restaurant: Restaurant;
    onClose: () => void;
    onToggleFavorite: (restaurantId: string) => void;
    isFromFavorites?: boolean;
}

const RestaurantModal: React.FC<RestaurantModalProps> = ({ restaurant, onClose, onToggleFavorite, isFromFavorites }) => {
    const [newReview, setNewReview] = useState({ rating: 1, content: '' });

    const handleAddReview = async () => {
        try {
            if (!newReview.rating || newReview.rating < 1 || newReview.rating > 5 || !newReview.content.trim()) {
                throw new Error("Please provide a rating between 1 and 5 and a review content.");
            }
            await addReview(restaurant.id, newReview);
            onClose();
            // You might want to refresh the restaurant details or update the reviews list here
        } catch (error: unknown) {
            console.error('Error adding review:', error);
            if (error instanceof Error) {
                alert(error.message);
            } else {
                alert('An error occurred while adding the review.');
            }
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[1000]">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto relative z-[1001] pointer-events-auto">
                <h2 className="text-2xl font-bold mb-4">{restaurant.name}</h2>
                <p className="text-gray-600 dark:text-gray-400 mb-2">{restaurant.address}</p>
                <p className="text-gray-600 dark:text-gray-400 mb-2">Category: {restaurant.category}</p>
                <div className="flex items-center mb-4">
                    <span className="text-yellow-400 mr-1">★</span>
                    <span>{restaurant.rating?.toFixed(1) || 'N/A'}</span>
                </div>
                {restaurant.photo_url && (
                    <img src={restaurant.photo_url} alt={restaurant.name} className="w-full h-48 object-cover mb-4 rounded" />
                )}
                <button
                    onClick={() => onToggleFavorite(restaurant.id)}
                    className={`w-full py-2 px-4 rounded text-white mb-4 ml-2 ${isFromFavorites || restaurant.isFavorite ? 'bg-blue-500 hover:bg-red-600' : 'bg-blue-500 hover:bg-blue-600'}`}
                >
                    {isFromFavorites || restaurant.isFavorite ? 'Remove from Favorites' : 'Add to Favorites'}
                </button>

                <div className="mb-6">
                    <h3 className="text-xl font-semibold mb-2">Add Your Review</h3>
                    <div className="mb-2">
                        <label className="block mb-1">Rating:</label>
                        <input
                            type="number"
                            min="1"
                            max="5"
                            value={newReview.rating}
                            onChange={(e) => setNewReview({ ...newReview, rating: parseInt(e.target.value) })}
                            className="w-full p-2 border rounded"
                        />
                    </div>
                    <div className="mb-2">
                        <label className="block mb-1">Review:</label>
                        <textarea
                            value={newReview.content}
                            onChange={(e) => setNewReview({ ...newReview, content: e.target.value })}
                            className="w-full p-2 border rounded"
                            rows={4}
                        ></textarea>
                    </div>
                    <button
                        onClick={handleAddReview}
                        className="bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600"
                    >
                        Submit Review
                    </button>
                </div>

                <h3 className="text-xl font-semibold mb-2">Reviews</h3>
                <div className="max-h-60 overflow-y-auto">
                    {restaurant.top_k_reviews && restaurant.top_k_reviews.length > 0 ? (
                        <>
                            <h4 className="font-semibold mb-2 mt-4">Custom Reviews</h4>
                            {restaurant.top_k_reviews.filter(review => !review.is_google_review).map((review: Review) => (
                                <div key={review.id} className="mb-4 border-b border-gray-200 dark:border-gray-700 pb-4">
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="font-semibold">{review.author}</span>
                                        <span className="text-yellow-400">{'★'.repeat(Math.round(review.rating))}</span>
                                    </div>
                                    <p className="text-gray-600 dark:text-gray-400">{review.content}</p>
                                </div>
                            ))}
                            <h4 className="font-semibold mb-2">Google Reviews</h4>
                            {restaurant.top_k_reviews.filter(review => review.is_google_review).map((review: Review) => (
                                <div key={review.id} className="mb-4 border-b border-gray-200 dark:border-gray-700 pb-4">
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="font-semibold">{review.author}</span>
                                        <span className="text-yellow-400">{'★'.repeat(Math.round(review.rating))}</span>
                                    </div>
                                    <p className="text-gray-600 dark:text-gray-400">{review.content}</p>
                                </div>
                            ))}

                        </>
                    ) : (
                        <p className="text-gray-600 dark:text-gray-400">No reviews available.</p>
                    )}
                </div>
                <button
                    onClick={onClose}
                    className="mt-4 bg-gray-300 dark:bg-gray-600 text-gray-800 dark:text-white py-2 px-4 rounded hover:bg-gray-400 dark:hover:bg-gray-700"
                >
                    Close
                </button>
            </div>
        </div>
    );

};

export default RestaurantModal;