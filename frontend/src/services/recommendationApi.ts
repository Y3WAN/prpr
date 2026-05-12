import api from './api';

export interface Recommendation {
  truck_id: number;
  truck_name: string;
  food_type: string;
  distance_m: number;
  latitude: number;
  longitude: number;
}

export const recommendationApi = {
  get: (lat: number, lng: number) =>
    api.get<Recommendation | null>('/recommendations', { params: { lat, lng } }),
};
