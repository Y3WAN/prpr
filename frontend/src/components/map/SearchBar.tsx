import { useEffect, useRef, useState } from 'react';
import type { FoodTruck } from '../../types/truck';
import { useTruckStore } from '../../stores/truckStore';
import { useMapStore } from '../../stores/mapStore';
import { useLocationStore } from '../../stores/locationStore';

interface KakaoPlace {
  id: string;
  place_name: string;
  category_name: string;
  address_name: string;
  road_address_name: string;
  x: string; // 경도
  y: string; // 위도
}

const calcDistance = (lat1: number, lng1: number, lat2: number, lng2: number) => {
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLng / 2) ** 2;
  const km = R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return km < 1 ? `${Math.round(km * 1000)}m` : `${km.toFixed(1)}km`;
};

// Kakao Places 서비스 인스턴스를 지연 초기화
const psRef = { current: null as any };
const getPS = () => {
  if (!psRef.current && window.kakao?.maps?.services) {
    psRef.current = new window.kakao.maps.services.Places();
  }
  return psRef.current;
};

export const SearchBar = () => {
  const [query, setQuery] = useState('');
  const [truckResults, setTruckResults] = useState<FoodTruck[]>([]);
  const [placeResults, setPlaceResults] = useState<KakaoPlace[]>([]);
  const [open, setOpen] = useState(false);

  const { trucks } = useTruckStore();
  const { setCenter, setSelectedTruck } = useMapStore();
  const { userLocation } = useLocationStore();
  const inputRef = useRef<HTMLInputElement>(null);
  const wrapRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // 트럭 로컬 필터
  useEffect(() => {
    const q = query.trim().toLowerCase();
    if (!q) { setTruckResults([]); return; }
    setTruckResults(
      trucks.filter(
        (t) =>
          t.name.toLowerCase().includes(q) ||
          t.menus.some((m) => m.name.toLowerCase().includes(q)) ||
          t.representative_menu?.toLowerCase().includes(q),
      ),
    );
  }, [query, trucks]);

  // Kakao Places 지역 검색 (디바운스 300ms)
  useEffect(() => {
    let cancelled = false;
    if (debounceRef.current) clearTimeout(debounceRef.current);

    const q = query.trim();
    if (!q) { setPlaceResults([]); return; }

    debounceRef.current = setTimeout(() => {
      const ps = getPS();
      if (!ps) return;
      ps.keywordSearch(q, (data: KakaoPlace[], status: string) => {
        if (cancelled) return;
        if (status === window.kakao.maps.services.Status.OK) {
          setPlaceResults(data.slice(0, 5));
        } else {
          setPlaceResults([]);
        }
      });
    }, 300);

    return () => {
      cancelled = true;
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [query]);

  // 바깥 클릭 시 드롭다운 닫기
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleTruckSelect = (truck: FoodTruck) => {
    setCenter({ lat: truck.latitude, lng: truck.longitude });
    setSelectedTruck(truck);
    setQuery('');
    setOpen(false);
  };

  const handlePlaceSelect = (place: KakaoPlace) => {
    setCenter({ lat: parseFloat(place.y), lng: parseFloat(place.x) });
    setQuery('');
    setOpen(false);
  };

  const hasResults = truckResults.length > 0 || placeResults.length > 0;
  const showDropdown = open && query.trim().length > 0;

  return (
    <div className="search-bar" ref={wrapRef}>
      <div className="search-input-wrap">
        <span className="search-icon">🔍</span>
        <input
          ref={inputRef}
          className="search-input"
          placeholder="지역명, 역, 가게명으로 검색"
          value={query}
          onChange={(e) => { setQuery(e.target.value); setOpen(true); }}
          onFocus={() => setOpen(true)}
        />
        {query && (
          <button
            className="search-clear"
            onMouseDown={(e) => {
              e.preventDefault();
              setQuery('');
              setTruckResults([]);
              setPlaceResults([]);
              inputRef.current?.focus();
            }}
          >
            ✕
          </button>
        )}
      </div>

      {showDropdown && (
        <ul className="search-results">
          {!hasResults && (
            <li className="search-no-result">검색 결과가 없습니다</li>
          )}

          {placeResults.length > 0 && (
            <>
              <li className="search-section-header">📍 장소</li>
              {placeResults.map((place) => {
                const category = place.category_name.split(' > ')[0];
                const address = place.road_address_name || place.address_name;
                return (
                  <li
                    key={place.id}
                    className="search-result-item"
                    onMouseDown={() => handlePlaceSelect(place)}
                  >
                    <div className="search-result__header">
                      <span className="search-result__name">{place.place_name}</span>
                      {category && (
                        <span className="search-place-category">{category}</span>
                      )}
                    </div>
                    {address && (
                      <div className="search-result__info">
                        <span className="search-result__menu">{address}</span>
                      </div>
                    )}
                  </li>
                );
              })}
            </>
          )}

          {truckResults.length > 0 && (
            <>
              <li className="search-section-header">🚚 가게</li>
              {truckResults.map((truck) => {
                const q = query.trim().toLowerCase();
                const matchedMenus = truck.menus
                  .filter((m) => m.name.toLowerCase().includes(q))
                  .slice(0, 2)
                  .map((m) => m.name)
                  .join(', ');
                const dist = userLocation
                  ? calcDistance(userLocation.lat, userLocation.lng, truck.latitude, truck.longitude)
                  : null;
                return (
                  <li
                    key={truck.id}
                    className="search-result-item"
                    onMouseDown={() => handleTruckSelect(truck)}
                  >
                    <div className="search-result__header">
                      <span className="search-result__name">{truck.name}</span>
                      <span className={`truck-badge truck-badge--${truck.is_open ? 'open' : 'closed'}`}>
                        {truck.is_open ? '영업중' : '영업종료'}
                      </span>
                    </div>
                    <div className="search-result__info">
                      <span className="search-result__menu">
                        {matchedMenus || truck.representative_menu || ''}
                      </span>
                      {dist && <span className="search-result__dist">{dist}</span>}
                    </div>
                  </li>
                );
              })}
            </>
          )}
        </ul>
      )}
    </div>
  );
};
