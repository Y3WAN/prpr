import { useRef } from 'react';
import type { FoodTruck, LatLng } from '../../types/truck';
import { useKakaoMap } from '../../hooks/useKakaoMap';

interface Props {
  center: LatLng;
  trucks: FoodTruck[];
  onMarkerClick: (truck: FoodTruck) => void;
  userLocation: LatLng | null;
}

export const KakaoMap = ({ center, trucks, onMarkerClick, userLocation }: Props) => {
  const mapRef = useRef<HTMLDivElement>(null);
  useKakaoMap(mapRef, center, trucks, onMarkerClick, userLocation);

  return <div ref={mapRef} className="kakao-map" />;
};
