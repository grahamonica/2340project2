import React, { useState, useEffect } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css'; // Custom styles
import MapComponent from './MapComponent';
import FavoritesPage from './FavoritesPage'; // Import Favorites Page 
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom'; // Import React Router
import ContactUsPage from './ContactUsPage'; // Import Contact Us Page

const App = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [restaurants, setRestaurants] = useState([]);
  const [filteredRestaurants, setFilteredRestaurants] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [darkMode, setDarkMode] = useState(false);
  const [cuisineFilter, setCuisineFilter] = useState('');

  const apiKey = 'AIzaSyB3fw32yga_uOdiVOYDYDIu-Q-tcntytnc'; // Google Maps API Key

  // Load saved favorites from local storage on initial render
  useEffect(() => {
    const savedFavorites = JSON.parse(localStorage.getItem('favorites')) || [];
    setFavorites(savedFavorites);
  }, []);

  // Fetch restaurants whenever searchQuery or cuisineFilter changes
  useEffect(() => {
    if (searchQuery) {
      fetchRestaurants();
    }
  }, [searchQuery, cuisineFilter]);

  const handleLogout = () => {
    // Placeholder for logout logic (will be integrated with backend later)
    console.log("User logged out");
    // Perform additional actions like redirecting to a login page or clearing local storage
  };  

  const fetchRestaurants = async () => {
    try {
      const location = '33.7490,-84.3880'; // Atlanta Coordinates as an example (latitude,longitude)
      const radius = 1500; // Search radius in meters
      const response = await axios.get(
        `https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=${location}&radius=${radius}&type=restaurant&keyword=${searchQuery}&key=${apiKey}`
      );

      const places = response.data.results.map(place => ({
        name: place.name,
        location: place.vicinity,
        rating: place.rating || 0, // Default to 0 if rating is missing
        cuisine: place.types.includes('restaurant') ? 'Restaurant' : 'Other', // Simple mapping for cuisine
      }));

      // Set the restaurants fetched and filtered data
      setRestaurants(places);
      filterRestaurants(places);
    } catch (error) {
      console.error('Error fetching data from Google Maps API', error);
    }
  };

  const filterRestaurants = (places) => {
    const filtered = (places || restaurants).filter(restaurant =>
      restaurant.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
      (cuisineFilter ? restaurant.cuisine === cuisineFilter : true)
    );
    setFilteredRestaurants(filtered);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchRestaurants();
  };

  const toggleFavorite = (restaurant) => {
    let updatedFavorites = [...favorites];
    if (favorites.some(fav => fav.name === restaurant.name)) {
      updatedFavorites = updatedFavorites.filter(fav => fav.name !== restaurant.name);
    } else {
      updatedFavorites.push(restaurant);
    }
    setFavorites(updatedFavorites);
    localStorage.setItem('favorites', JSON.stringify(updatedFavorites));
  };

  return (
    <Router>
      <div className={darkMode ? 'app-theme-dark' : 'app-theme-light'}>
        {/* Dark Mode Toggle and Logout Button */}
        <div className="container d-flex justify-content-end my-2">
          <button className="btn btn-sm btn-outline-secondary mx-2" onClick={() => setDarkMode(!darkMode)}>
            {darkMode ? 'Light Mode' : 'Dark Mode'}
          </button>
          <button className="btn btn-sm btn-outline-danger" onClick={() => handleLogout()}>
            Logout
          </button>
        </div>

        {/* Navbar */}
        <nav className="navbar navbar-expand-lg navbar-dark bg-primary">
          <a className="navbar-brand" href="/">🍽 Restaurant Finder</a>
          <div className="collapse navbar-collapse">
            <ul className="navbar-nav ml-auto">
              <li className="nav-item">
                <Link className="nav-link" to="/">Home</Link> {/* Change to Link for navigation */}
              </li>
              <li className="nav-item">
                <Link className="nav-link" to="/favorites">Favorites</Link> {/* Change to Link for navigation */}
              </li>
              <li className="nav-item">
                <Link className="nav-link" to="/contact">Contact Us</Link> {/* Change to Link for navigation */}
              </li>
            </ul>
          </div>
        </nav>
  
        {/* Routes */}
        <Routes>

          <Route path="/" element={
            <div className="container my-4">
              {/* Home Page with Restaurant Finder */}
              <header className="my-4 text-center">
                <h1 className="display-4">Find the Best Restaurants Near You</h1>
              </header>
              <form onSubmit={handleSearch} className="mb-4">
                <div className="input-group">
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Search for a restaurant..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                  <button type="submit" className="btn btn-success">Search</button>
                </div>
              </form>

              {/* Sort by Cuisines Bar */}
              <div className="sort-cuisines-bar bg-light p-3 rounded">
                <h5 className="mb-3 text-center">Sort by Cuisines</h5>
                <div className="d-flex justify-content-center flex-wrap">
                  <button className="btn btn-outline-secondary m-2" onClick={() => setCuisineFilter('')}>All</button>
                  <button className="btn btn-outline-primary m-2" onClick={() => setCuisineFilter('Italian')}>Italian</button>
                  <button className="btn btn-outline-success m-2" onClick={() => setCuisineFilter('Japanese')}>Japanese</button>
                  <button className="btn btn-outline-warning m-2" onClick={() => setCuisineFilter('American')}>American</button>
                  <button className="btn btn-outline-danger m-2" onClick={() => setCuisineFilter('Mexican')}>Mexican</button>
                  <button className="btn btn-outline-info m-2" onClick={() => setCuisineFilter('Vegan')}>Vegan</button>
                  <button className="btn btn-outline-secondary m-2" onClick={() => setCuisineFilter('Indian')}>Indian</button>
                  <button className="btn btn-outline-dark m-2" onClick={() => setCuisineFilter('Barbecue')}>Barbecue</button>
                  <button className="btn btn-outline-dark m-2" onClick={() => setCuisineFilter('Chinese')}>Chinese</button>
                </div>
              </div>

              {/* Restaurant Results */}
              <div className="row">
                {filteredRestaurants.length ? (
                  filteredRestaurants.map((restaurant, index) => (
                    <div className="col-md-4 mb-4" key={index}>
                      <div className="card h-100">
                        <div className="card-body">
                          <h5 className="card-title">{restaurant.name}</h5>
                          <p className="card-text">{restaurant.cuisine} Cuisine</p>
                          <p className="card-text"><small className="text-muted">{restaurant.location}</small></p>
                          <div className="rating mt-2">
                            {Array.from({ length: Math.floor(restaurant.rating) }, (_, i) => (
                              <span key={i} className="text-warning">★</span>
                            ))}
                            {restaurant.rating % 1 > 0 && <span className="text-warning">☆</span>}
                          </div>
                        </div>
                        <div className="card-footer text-center">
                          <button className="btn btn-primary">View Details</button>
                          <button className="btn btn-outline-secondary ml-2" onClick={() => toggleFavorite(restaurant)}>
                            {favorites.some(fav => fav.name === restaurant.name) ? 'Remove from Favorites' : 'Add to Favorites'}
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <p>No results found. Please try a different search.</p>
                )}
              </div>

              {/* MapComponent */}
              <MapComponent restaurants={filteredRestaurants} />
            </div>
          } />
          <Route path="/favorites" element={<FavoritesPage favorites={favorites} toggleFavorite={toggleFavorite} />} />
           <Route path="/contact" element={<ContactUsPage />} />
        </Routes>
        {/* Footer */}
        <footer className="bg-dark text-white text-center py-3">
          <p>&copy; 2024 Restaurant Finder. All Rights Reserved.</p>
          <a href="#" className="text-white mx-2">Privacy Policy</a> | 
          <a href="#" className="text-white mx-2">Terms of Service</a>
        </footer>
      </div>
    </Router>
  );

}
export default App;
