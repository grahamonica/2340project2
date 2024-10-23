"use client";

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import React, { useEffect, useState } from 'react';
import DarkModeToggle from './components/DarkModeToggle';
import FilterComponent from './components/Filter';
import { useAuth } from './contexts/AuthContext';
import { searchRestaurants, toggleFavorite } from './utils/api';
import { Restaurant } from './utils/schema';

import dynamic from 'next/dynamic';

export default function Home() {
  const RestaurantMap = dynamic(() => import('./components/RestaurantMap'), { ssr: false });
  const { user, logout, isAuthenticated } = useAuth();
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState('');
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [availableCuisines, setAvailableCuisines] = useState<string[]>(['All', 'Italian', 'Thai','Chinese','Mexican', 'American' ]);
  const [filteredRestaurants, setFilteredRestaurants] = useState<Restaurant[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentLocation, setCurrentLocation] = useState<{ latitude: number; longitude: number } | null>(null);

  const [filters, setFilters] = useState({
    cuisine: 'All',
    distance: 50,
    rating: 0,
    location: 'Georgia Tech',
  });

  const handleLogout = async () => {
    try {
      await logout();
      router.push('/login');
    } catch (error) {
      console.error('Logout failed', error);
    }
  };

  const handleSearch = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
  
    try {
      // We are not using cuisine anymore, so no need to check for cuisine filter
      // Only pass the distance and rating filters
      const results = await searchRestaurants(
        searchTerm,
        undefined, // Pass undefined or remove this parameter if cuisine is no longer needed
        filters.distance,
        filters.rating
      );
  
      console.log('Search results:', results);
      setRestaurants(results);
      setFilteredRestaurants(results);
    } catch (error) {
      console.error('Error searching restaurants:', error);
    } finally {
      setIsLoading(false);
    }
  };
  

  const handleFilterChange = (name: string, value: string | number) => {
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const handleToggleFavorite = async (restaurantId: string) => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    try {
      const response = await toggleFavorite(restaurantId);
      console.log(response.message);

      setFilteredRestaurants(prevRestaurants =>
        prevRestaurants.map(restaurant =>
          restaurant.id === restaurantId
            ? { ...restaurant, isFavorite: !restaurant.isFavorite }
            : restaurant
        )
      );

      setRestaurants(prevRestaurants =>
        prevRestaurants.map(restaurant =>
          restaurant.id === restaurantId
            ? { ...restaurant, isFavorite: !restaurant.isFavorite }
            : restaurant
        )
      );
    } catch (error) {
      console.error('Error toggling favorite:', error);
    }
  };


  useEffect(() => {
    if (restaurants.length > 0) {
      const cuisines = ['All', ...Array.from(new Set(restaurants.map(r => r.category)))];
      setAvailableCuisines(cuisines);
    }
  }, [restaurants]);

  useEffect(() => {
    console.log('Current filters:', filters);
    console.log('Restaurants to filter:', restaurants);

    const filtered = restaurants.filter(restaurant => {
      const cuisineMatch = filters.cuisine === 'All' || restaurant.category.toLowerCase().includes(filters.cuisine.toLowerCase());
      const ratingMatch = restaurant.rating !== null && restaurant.rating >= filters.rating;
      const distanceMatch = restaurant.distance_from_base <= filters.distance;

      console.log(`Restaurant: ${restaurant.name}`);
      console.log(`Cuisine match: ${cuisineMatch}, Rating match: ${ratingMatch}, Distance match: ${distanceMatch}`);
      console.log(`Distance: ${restaurant.distance_from_base}, Filter distance: ${filters.distance}`);

      return cuisineMatch && ratingMatch && distanceMatch;
    });

    console.log('Filtered restaurants:', filtered);
    setFilteredRestaurants(filtered);
  }, [filters, restaurants]);

  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground">
      {/* Header */}
      <header className="sticky top-0 bg-white dark:bg-black w-full text-card-foreground p-4 z-50">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">🍽 Restaurant Finder</h1>
          <nav className="flex items-center space-x-4">
            <Link href="/" className="hover:underline">Home</Link>
            <Link href="/profile" className="hover:underline">Profile</Link>
            <DarkModeToggle />
            {isAuthenticated ? (
              <button onClick={handleLogout} className="hover:underline">Logout</button>
            ) : (
              <Link href="/login" className="hover:underline">Login</Link>
            )}
          </nav>        </div>
      </header>

      {/* Background Image for Light and Dark Mode */}
      <div className="relative w-full">
        {/* Regular skyline for light mode */}
        <img
          src="/assets/daytime-2.jpg"
          alt="Atlanta Skyline"
          className="w-full h-full object-cover object-top block dark:hidden"
        />
        {/* Dark skyline for dark mode */}
        <img
          src="/assets/nightime-2.jpg"
          alt="Atlanta Skyline"
          className="w-full h-full object-cover object-top hidden dark:block"
        />
      </div>

      {/* Main Content */}
      <main className="absolute inset-20 flex-grow container mx-auto px-4 py-8">
        {user ? (
          <h2 className="text-3xl font-bold text-center mb-8"></h2>
        ) : (
          <h2 className="text-4xl mb-20"></h2>
        )}
        <h2 className="text-5xl text-center mb-4 mt-20 dark:text-shadow-black text-shadow-white">
  Welcome to Restaurant Finder!
</h2>

<h2 className="text-3xl font-bold text-center mb-8 mt-20 dark:text-shadow-black text-shadow-white">
  Find the Best Restaurants Near You
</h2>


        {/* Search Form */}
        <form onSubmit={handleSearch} className="mb-41, mt-25">
          <div className="flex">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search for a restaurant..."
              className="flex-grow p-2 border border-gray-200 rounded-l-md focus:outline-none focus:ring-4 focus:ring-blue-500 bg-input-background text-input-foreground"
            />
            <button
              type="submit"
              className="bg-button-background text-button-foreground px-4 py-2 rounded-r-md hover:bg-opacity-90 focus:outline-none focus:ring-4 focus:ring-blue-500 flex items-center"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Searching...
                </>
              ) : (
                'Search'
              )}
            </button>
          </div>
        </form>

        {/* Filter Component */}
        <FilterComponent
          filters={filters}
          availableCuisines={availableCuisines}
          onFilterChange={handleFilterChange}
        />

        {/* Restaurant Results
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredRestaurants.map((restaurant) => (
            <div key={restaurant.id} className="bg-card-background text-card-foreground rounded-lg shadow-md overflow-hidden">
              <div className="p-4">
                <h3 className="text-xl font-semibold mb-2">{restaurant.name}</h3>
                <p className="text-gray-600 dark:text-gray-400 mb-2">{restaurant.category}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">{restaurant.address}</p>
                <div className="flex items-center mb-4">
                  {[...Array(5)].map((_, i) => (
                    <svg key={i} className={`w-5 h-5 ${i < Math.floor(restaurant.rating || 0) ? 'text-yellow-400' : 'text-gray-300 dark:text-gray-600'} fill-current`} viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                  <span className="ml-2 text-gray-600 dark:text-gray-400">{restaurant.rating?.toFixed(1)}</span>
                </div>
                <div className="flex justify-between">
                  <button className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500">
                    View Details
                  </button>
                  <button
                    onClick={() => handleToggleFavorite(restaurant.id)}
                    className="bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-200 px-4 py-2 rounded hover:bg-gray-300 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-400"
                  >
                    {restaurant.isFavorite ? 'Remove from Favorites' : 'Add to Favorites'}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div> */}
      </main>

      {(
        <div className="mt-4">
          <RestaurantMap
            restaurants={filteredRestaurants}
            center={[33.7756, -84.3963]} // Coordinates for Georgia Tech
            onToggleFavorite={handleToggleFavorite}
          />
        </div>
      )}

      {/* Footer */}
      <footer className="bg-card-background text-card-foreground py-4">
        <div className="container mx-auto text-center">
          <p>&copy; 2024 Restaurant Finder. All Rights Reserved.</p>
          <div className="mt-2">
            <a href="#" className="text-gray-400 hover:text-foreground mx-2">Privacy Policy</a> |
            <a href="#" className="text-gray-400 hover:text-foreground mx-2">Terms of Service</a>
          </div>
        </div>
      </footer>
    </div>
  );
}