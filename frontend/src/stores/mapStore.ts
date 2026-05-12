import { create } from 'zustand';
import type { FoodTruck, LatLng } from '../types/truck';
import { DEFAULT_CENTER } from '../constants/map';

interface MapState {
  center: LatLng;
  selectedTruck: FoodTruck | null;
  isSidebarOpen: boolean;
  setCenter: (center: LatLng) => void;
  setSelectedTruck: (truck: FoodTruck | null) => void;
  openSidebar: () => void;
  closeSidebar: () => void;
}

export const useMapStore = create<MapState>((set) => ({
  center: DEFAULT_CENTER,
  selectedTruck: null,
  isSidebarOpen: false,

  setCenter: (center) => set({ center }),
  setSelectedTruck: (truck) => set({ selectedTruck: truck }),
  openSidebar: () => set({ isSidebarOpen: true }),
  closeSidebar: () => set({ isSidebarOpen: false }),
}));
