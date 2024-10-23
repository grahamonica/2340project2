import React, { useEffect } from 'react';

const MapComponent = ({ restaurants }) => {
  useEffect(() => {
    // Load the map once the component mounts
    const map = new window.google.maps.Map(document.getElementById('map'), {
      center: { lat: 33.7490, lng: -84.3880 }, // Initial center (Atlanta, for example)
      zoom: 13, // Zoom level
    });

    // Plot markers for each restaurant
    restaurants.forEach((restaurant) => {
      const marker = new window.google.maps.Marker({
        position: {
          lat: restaurant.latitude, // Make sure your restaurants array includes latitude
          lng: restaurant.longitude, // Make sure your restaurants array includes longitude
        },
        map: map,
        title: restaurant.name, // Optional title for the marker
      });

      // Optional: Add info windows for markers
      const infoWindow = new window.google.maps.InfoWindow({
        content: `<h4>${restaurant.name}</h4><p>${restaurant.location}</p>`,
      });

      marker.addListener('click', () => {
        infoWindow.open(map, marker);
      });
    });
  }, [restaurants]);

  return (
    <div id="map" style={{ width: '100%', height: '400px' }}>
      {/* The map will render here */}
    </div>
  );
};

export default MapComponent;
