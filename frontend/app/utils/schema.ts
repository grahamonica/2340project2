export interface Restaurant {
  id: string;
  name: string;
  address: string;
  latitude: number;
  longitude: number;
  category: string;
  rating: number | null;
  distance_from_base: number;
  isFavorite?: boolean;
  photo_url?: string;
  top_k_reviews?: Review[];
}

// ... rest of the file remains the same
export interface Review {
  id: number;
  author: string;
  title: string;
  content: string;
  rating: number;
  created_at: string;
  is_google_review: boolean;
}
