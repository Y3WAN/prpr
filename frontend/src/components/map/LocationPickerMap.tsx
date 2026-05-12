import { useEffect, useRef } from 'react';

interface Props {
  lat: string;
  lng: string;
  onChange: (lat: string, lng: string) => void;
}

export const LocationPickerMap = ({ lat, lng, onChange }: Props) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<any>(null);
  const markerRef = useRef<any>(null);
  const isExternalUpdate = useRef(false);

  useEffect(() => {
    if (!mapRef.current || !window.kakao) return;
    if (mapInstance.current) return;

    window.kakao.maps.load(() => {
      if (!mapRef.current || mapInstance.current) return;

      const initLat = lat ? Number(lat) : 37.5665;
      const initLng = lng ? Number(lng) : 126.9780;
      const center = new window.kakao.maps.LatLng(initLat, initLng);

      const map = new window.kakao.maps.Map(mapRef.current, { center, level: 4 });
      mapInstance.current = map;

      const marker = new window.kakao.maps.Marker({ position: center, map, draggable: true });
      markerRef.current = marker;

      window.kakao.maps.event.addListener(map, 'click', (e: any) => {
        const pos = e.latLng;
        marker.setPosition(pos);
        isExternalUpdate.current = true;
        onChange(String(pos.getLat()), String(pos.getLng()));
      });

      window.kakao.maps.event.addListener(marker, 'dragend', () => {
        const pos = marker.getPosition();
        isExternalUpdate.current = true;
        onChange(String(pos.getLat()), String(pos.getLng()));
      });
    });
  }, []);

  useEffect(() => {
    if (!mapInstance.current || !markerRef.current || !window.kakao) return;
    if (isExternalUpdate.current) {
      isExternalUpdate.current = false;
      return;
    }
    if (!lat || !lng) return;
    const pos = new window.kakao.maps.LatLng(Number(lat), Number(lng));
    markerRef.current.setPosition(pos);
    mapInstance.current.panTo(pos);
  }, [lat, lng]);

  return (
    <div className="location-picker-wrap">
      <div ref={mapRef} className="location-picker-map" />
      <p className="location-picker-hint">지도를 클릭하거나 마커를 드래그해 위치를 지정하세요</p>
    </div>
  );
};
