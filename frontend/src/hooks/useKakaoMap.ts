import { type RefObject, useEffect, useRef, useState } from 'react';
import type { FoodTruck, LatLng } from '../types/truck';
import { useMapStore } from '../stores/mapStore';
import { getTruckEmoji } from '../utils/truckCategory';

declare global {
  interface Window {
    kakao: any;
  }
}

export const useKakaoMap = (
  mapRef: RefObject<HTMLDivElement | null>,
  center: LatLng,
  trucks: FoodTruck[],
  onMarkerClick: (truck: FoodTruck) => void,
  userLocation: LatLng | null,
) => {
  const mapInstance = useRef<any>(null);
  const overlayMapRef = useRef<Map<number, any>>(new Map());
  const userOverlayRef = useRef<any>(null);
  const isMapMovingRef = useRef(false);
  const [mapReady, setMapReady] = useState(false);
  const { setCenter } = useMapStore();

  useEffect(() => {
    if (!mapRef.current || !window.kakao) return;
    if (mapInstance.current) return;

    let cancelled = false;

    window.kakao.maps.load(() => {
      if (cancelled || !mapRef.current || mapInstance.current) return;

      const map = new window.kakao.maps.Map(mapRef.current, {
        center: new window.kakao.maps.LatLng(center.lat, center.lng),
        level: 5,
      });
      mapInstance.current = map;
      setMapReady(true);

      window.kakao.maps.event.addListener(map, 'dragend', () => {
        const c = map.getCenter();
        isMapMovingRef.current = true;
        requestAnimationFrame(() => {
          setCenter({ lat: c.getLat(), lng: c.getLng() });
        });
      });

      let zoomTimer: ReturnType<typeof setTimeout> | null = null;
      window.kakao.maps.event.addListener(map, 'zoom_changed', () => {
        isMapMovingRef.current = true;
        if (zoomTimer) clearTimeout(zoomTimer);
        zoomTimer = setTimeout(() => {
          const c = map.getCenter();
          setCenter({ lat: c.getLat(), lng: c.getLng() });
          zoomTimer = null;
        }, 350);
      });
    });

    return () => {
      cancelled = true;
      overlayMapRef.current.clear();
      userOverlayRef.current = null;
      mapInstance.current = null;
      setMapReady(false);
    };
  }, []);

  useEffect(() => {
    if (!mapInstance.current || !window.kakao) return;

    const newIds = new Set(trucks.map((t) => t.id));

    overlayMapRef.current.forEach((overlay, id) => {
      if (!newIds.has(id)) {
        overlay.setMap(null);
        overlayMapRef.current.delete(id);
      }
    });

    trucks.forEach((truck) => {
      if (overlayMapRef.current.has(truck.id)) return;

      const pos = new window.kakao.maps.LatLng(truck.latitude, truck.longitude);
      const emoji = getTruckEmoji(truck);

      const content = document.createElement('div');
      content.className = 'truck-marker';
      content.innerHTML = `
        <div class="truck-marker__name">${truck.name}</div>
        <div class="truck-marker__bubble">${emoji}</div>
        <div class="truck-marker__tail"></div>
      `;
      content.addEventListener('click', () => onMarkerClick(truck));

      const overlay = new window.kakao.maps.CustomOverlay({
        position: pos,
        content,
        xAnchor: 0.5,
        yAnchor: 1.0,
        zIndex: 3,
      });
      overlay.setMap(mapInstance.current);
      overlayMapRef.current.set(truck.id, overlay);
    });
  }, [trucks, mapReady]);

  useEffect(() => {
    if (!mapInstance.current || !window.kakao) return;
    if (isMapMovingRef.current) {
      isMapMovingRef.current = false;
      return;
    }
    mapInstance.current.panTo(new window.kakao.maps.LatLng(center.lat, center.lng));
  }, [center]);

  useEffect(() => {
    if (!mapInstance.current || !window.kakao) return;

    if (userOverlayRef.current) {
      userOverlayRef.current.setMap(null);
      userOverlayRef.current = null;
    }

    if (!userLocation) return;

    const pos = new window.kakao.maps.LatLng(userLocation.lat, userLocation.lng);
    userOverlayRef.current = new window.kakao.maps.CustomOverlay({
      position: pos,
      content: '<div class="user-location-marker"><div class="user-location-pulse"></div><div class="user-location-dot"></div></div>',
      xAnchor: 0.5,
      yAnchor: 0.5,
      zIndex: 10,
    });
    userOverlayRef.current.setMap(mapInstance.current);
  }, [userLocation]);

  return mapInstance;
};
