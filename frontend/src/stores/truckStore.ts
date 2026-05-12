import { create } from 'zustand';
import type { FoodTruck } from '../types/truck';
import api from '../services/api';

interface TruckState {
  trucks: FoodTruck[];
  isLoading: boolean;
  hasFetched: boolean;
  error: string | null;
  fetchTrucks: (params: { lat: number; lng: number; radius?: number }) => Promise<void>;
}

export const useTruckStore = create<TruckState>((set) => ({
  trucks: [],
  isLoading: false,
  hasFetched: false,
  error: null,

  fetchTrucks: async ({ lat, lng, radius = 2000 }) => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await api.get('/trucks', { params: { lat, lng, radius } });
      set({ trucks: data, hasFetched: true });
    } catch {
      set({ error: '데이터를 불러오는 데 실패했습니다.', hasFetched: true });
    } finally {
      set({ isLoading: false });
    }
  },
}));
