import { Icon } from 'leaflet';
import { useRouter } from 'next/navigation';
import React, { useEffect, useState } from 'react';
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet';
import { useAuth } from '../contexts/AuthContext';
import { Restaurant } from '../utils/schema';
import RestaurantModal from './RestaurantModal';

interface RestaurantMapProps {
    restaurants: Restaurant[];
    center: [number, number];
    onToggleFavorite: (restaurantId: string) => void;
}

const MapUpdater: React.FC<{ center: [number, number] }> = ({ center }) => {
    const map = useMap();

    useEffect(() => {
        map.setView(center, map.getZoom());
    }, [map, center]);

    return null;
};

const RestaurantMap: React.FC<RestaurantMapProps> = ({ restaurants, center, onToggleFavorite }) => {
    const { isAuthenticated } = useAuth();
    const router = useRouter();
    const [selectedRestaurant, setSelectedRestaurant] = useState<Restaurant | null>(null);
    const [localRestaurants, setLocalRestaurants] = useState(restaurants);

    useEffect(() => {
        setLocalRestaurants(restaurants);
    }, [restaurants]);

    const handleToggleFavorite = async (restaurantId: string) => {
        if (!isAuthenticated) {
            router.push('/login');
            return;
        }
        onToggleFavorite(restaurantId);

        if (selectedRestaurant && selectedRestaurant.id === restaurantId) {
            setSelectedRestaurant(prevRestaurant => ({
                ...prevRestaurant!,
                isFavorite: !prevRestaurant!.isFavorite
            }));
        }
    };

    const handleCloseModal = () => {
        setSelectedRestaurant(null);
    };

    const customIcon = new Icon({
        iconUrl: '/assets/marker.svg',
        shadowUrl: '/assets/marker-shadow.svg',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41],
        shadowAnchor: [12, 41],
    });

    return (
        <div style={{ padding: '4rem', marginTop: '50px'  }}>
            <MapContainer center={center} zoom={13} style={{ height: '70vh', width: '100%', borderRadius: '20px', // Rounds the corners
    boxShadow: '0px 0px 20px rgba(0, 0, 0, 0.3)', }}>
                <MapUpdater center={center} />
                <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                />
                {localRestaurants.map((restaurant) => (
                    <Marker
                        key={restaurant.id}
                        position={[restaurant.latitude, restaurant.longitude]}
                        icon={customIcon}
                    >
                        <Popup>
                            <div style={{ maxWidth: '250px' }}>
                                <h3 className="text-lg font-semibold mb-1">{restaurant.name}</h3>
                                <p className="text-sm mb-1"><strong>Rating:</strong> {restaurant.rating} ⭐</p>
                                <button
                                    onClick={() => setSelectedRestaurant(restaurant)}
                                    className="w-full py-2 px-4 rounded text-white bg-blue-500 hover:bg-blue-600"
                                >
                                    View Details
                                </button>
                            </div>
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>
            {selectedRestaurant && (
                <RestaurantModal
                    restaurant={selectedRestaurant}
                    onClose={handleCloseModal}
                    onToggleFavorite={handleToggleFavorite}
                />
            )}
        </div>
    );
};

export default RestaurantMap;