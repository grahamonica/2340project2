import React from 'react';

const FavoritesPage = ({ favorites, toggleFavorite }) => {
  return (
    <div className="container my-5">
      <h1 className="text-center mb-4">Your Favorite Restaurants</h1>
      {favorites.length > 0 ? (
        <div className="row">
          {favorites.map((restaurant, index) => (
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
                  <button className="btn btn-outline-danger" onClick={() => toggleFavorite(restaurant)}>
                    Remove from Favorites
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-center">You have no favorite restaurants yet.</p>
      )}
    </div>
  );
};

export default FavoritesPage;
