import { create } from 'zustand';
import type { LatLng } from '../types/truck';
import { useMapStore } from './mapStore';

interface LocationState {
  userLocation: LatLng | null;
  locationError: string | null;
  requestLocation: () => void;
}

let watchId: number | null = null;
let hasCentered = false;

export const useLocationStore = create<LocationState>((set, get) => ({
  userLocation: null,
  locationError: null,

  requestLocation: () => {
    if (!navigator.geolocation) {
      set({ locationError: '이 브라우저에서는 GPS를 지원하지 않습니다.' });
      return;
    }

    const { userLocation } = get();
    if (userLocation) {
      useMapStore.getState().setCenter(userLocation);
    }

    if (watchId !== null) return;

    hasCentered = !!userLocation;

    watchId = navigator.geolocation.watchPosition(
      (pos) => {
        const location = { lat: pos.coords.latitude, lng: pos.coords.longitude };
        set({ userLocation: location, locationError: null });
        if (!hasCentered) {
          hasCentered = true;
          useMapStore.getState().setCenter(location);
        }
      },
      (err) => {
        if (err.code === err.PERMISSION_DENIED) {
          set({ locationError: '위치 권한이 거부되었습니다. 브라우저 설정에서 허용해주세요.' });
        } else {
          set({ locationError: '현재 위치를 확인할 수 없습니다.' });
        }
      },
      { enableHighAccuracy: true, maximumAge: 0, timeout: 10000 },
    );
  },
}));
