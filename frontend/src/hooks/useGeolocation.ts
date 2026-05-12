import { useEffect, useRef } from 'react';
import { useLocationStore } from '../stores/locationStore';
import { useTruckStore } from '../stores/truckStore';
import { useMapStore } from '../stores/mapStore';

export const useGeolocation = () => {
  const { requestLocation } = useLocationStore();
  const { fetchTrucks } = useTruckStore();
  const { center } = useMapStore();
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    requestLocation();
  }, []);

  useEffect(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      fetchTrucks({ lat: center.lat, lng: center.lng });
    }, 600);
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [center]);
};
