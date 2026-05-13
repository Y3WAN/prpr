import api from './api';
import type { FoodTruck } from '../types/truck';

export const truckApi = {
  list: (lat: number, lng: number, radius = 2000) =>
    api.get<FoodTruck[]>('/trucks', { params: { lat, lng, radius } }),

  get: (id: number) => api.get<FoodTruck>(`/trucks/${id}`),

  my: () => api.get<FoodTruck>('/trucks/my'),

  create: (data: { name: string; menus: { name: string; price: number }[]; latitude: number; longitude: number; description?: string; account_info?: string }) =>
    api.post<FoodTruck>('/trucks', data),

  updateLocation: (id: number, data: { latitude: number; longitude: number }) =>
    api.patch(`/trucks/${id}/location`, data),

  updateStatus: (id: number, is_open: boolean) =>
    api.patch(`/trucks/${id}/status`, { is_open }),

  keywords: (id: number) =>
    api.get<{ keywords: string[] }>(`/trucks/${id}/keywords`),

  nearest: (lat: number, lng: number) =>
    api.get<{ latitude: number | null; longitude: number | null }>('/trucks/nearest', { params: { lat, lng } }),

  updateMenus: (id: number, menus: { name: string; price: number }[]) =>
    api.patch<{ keywords: string[] }>(`/trucks/${id}/menus`, { menus }),

  deleteMy: () => api.delete('/trucks/my'),
};
