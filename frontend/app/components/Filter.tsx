import React from 'react';

interface FilterComponentProps {
  filters: {
    cuisine: string;
    distance: number;
    rating: number;
  };
  availableCuisines: string[];
  onFilterChange: (name: string, value: string | number) => void;
}

const FilterComponent: React.FC<FilterComponentProps> = ({ filters, availableCuisines, onFilterChange }) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    onFilterChange(name, name === 'distance' || name === 'rating' ? Number(value) : value);
  };

  return (
    <div className="mb-4 bg-card-background text-gray-800 dark:text-gray-200 p-4 rounded-lg shadow-lg dark:shadow-xl flex flex-wrap items-center gap-4">
      {/* Cuisine Filter (Commented out) */}
      {/* <div className="flex-1 min-w-[200px]">
        <label htmlFor="cuisine" className="block text-sm font-medium mb-1">Cuisine</label>
        <select
          id="cuisine"
          name="cuisine"
          value={filters.cuisine}
          onChange={handleChange}
          className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
        >
          {availableCuisines.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div> */}

      {/* Distance Filter */}
      <div className="flex-1 min-w-[200px]">
        <label htmlFor="distance" className="block text-sm font-medium mb-1">Distance: {filters.distance} miles</label>
        <input
          id="distance"
          type="range"
          name="distance"
          min="1"
          max="50"
          value={filters.distance}
          onChange={handleChange}
          className="w-full"
        />
      </div>

      {/* Rating Filter */}
      <div className="flex-1 min-w-[200px]">
        <label htmlFor="rating" className="block text-sm font-medium mb-1">Rating: {filters.rating} stars</label>
        <input
          id="rating"
          type="range"
          name="rating"
          min="0"
          max="5"
          step="0.5"
          value={filters.rating}
          onChange={handleChange}
          className="w-full"
        />
      </div>
    </div>
  );
};

export default FilterComponent;
