import { create } from 'zustand';
import type { LatLng } from '../types/truck';
import { useMapStore } from './mapStore';

interface LocationState {
  userLocation: LatLng | null;
  locationError: string | null;
  isLocating: boolean;
  requestLocation: () => void;
}

let watchId: number | null = null;
let hasCentered = false;

const GEO_OPTS: PositionOptions = { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 };

export const useLocationStore = create<LocationState>((set, get) => ({
  userLocation: null,
  locationError: null,
  isLocating: false,

  requestLocation: () => {
    if (!navigator.geolocation) {
      set({ locationError: '이 브라우저에서는 위치 서비스를 지원하지 않습니다.' });
      return;
    }

    const { userLocation } = get();

    // 이미 위치를 알고 있으면 지도만 이동
    if (userLocation) {
      useMapStore.getState().setCenter(userLocation);
      return;
    }

    // 위치 미확보 → getCurrentPosition으로 즉시 요청 (권한 재요청 포함)
    set({ isLocating: true, locationError: null });

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const location = { lat: pos.coords.latitude, lng: pos.coords.longitude };
        hasCentered = true;
        set({ userLocation: location, locationError: null, isLocating: false });
        useMapStore.getState().setCenter(location);
      },
      (err) => {
        const msg =
          err.code === err.PERMISSION_DENIED
            ? '위치 권한이 거부되었습니다. 브라우저 설정에서 허용해주세요.'
            : '현재 위치를 가져올 수 없습니다.';
        set({ locationError: msg, isLocating: false });
      },
      GEO_OPTS,
    );

    if (watchId !== null) return;

    // 백그라운드 위치 추적 시작
    watchId = navigator.geolocation.watchPosition(
      (pos) => {
        const location = { lat: pos.coords.latitude, lng: pos.coords.longitude };
        set({ userLocation: location, locationError: null });
        if (!hasCentered) {
          hasCentered = true;
          set({ isLocating: false });
          useMapStore.getState().setCenter(location);
        }
      },
      (err) => {
        if (err.code === err.PERMISSION_DENIED) {
          set({ locationError: '위치 권한이 거부되었습니다. 브라우저 설정에서 허용해주세요.' });
        }
        set({ isLocating: false });
      },
      GEO_OPTS,
    );
  },
}));
