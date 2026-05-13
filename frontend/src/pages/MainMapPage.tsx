import { useEffect, useRef } from 'react';
import { useMapStore } from '../stores/mapStore';
import { useTruckStore } from '../stores/truckStore';
import { useLocationStore } from '../stores/locationStore';
import { useWeatherStore } from '../stores/weatherStore';
import { useGeolocation } from '../hooks/useGeolocation';
import { KakaoMap } from '../components/map/KakaoMap';
import { SearchBar } from '../components/map/SearchBar';
import { CurrentLocationButton } from '../components/map/CurrentLocationButton';
import { WeatherToggleButton } from '../components/map/WeatherToggleButton';
import { NoTrucksNearby } from '../components/map/NoTrucksNearby';
import { PersonalRecommendation } from '../components/map/PersonalRecommendation';
import { RainOverlay } from '../components/map/RainOverlay';
import { FoodTruckBottomSheet } from '../components/truck/FoodTruckBottomSheet';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import type { FoodTruck } from '../types/truck';

const MainMapPage = () => {
  const { center, selectedTruck, setSelectedTruck } = useMapStore();
  const { trucks, isLoading, hasFetched } = useTruckStore();
  const { requestLocation, userLocation } = useLocationStore();
  const { isRaining, checked, checkWeather } = useWeatherStore();
  const weatherChecked = useRef(false);

  useGeolocation();

  useEffect(() => {
    if (userLocation && !weatherChecked.current) {
      weatherChecked.current = true;
      checkWeather(userLocation.lat, userLocation.lng);
    }
  }, [userLocation]);

  useEffect(() => {
    if (!checked) return;
    if (isRaining) {
      document.documentElement.classList.add('rainy');
    } else {
      document.documentElement.classList.remove('rainy');
    }
    return () => {
      document.documentElement.classList.remove('rainy');
    };
  }, [isRaining, checked]);

  const handleMarkerClick = (truck: FoodTruck) => {
    setSelectedTruck(truck);
  };

  return (
    <div className="map-container">
      {isRaining && <RainOverlay />}
      {!selectedTruck && <SearchBar />}
      <KakaoMap
        center={center}
        trucks={trucks}
        onMarkerClick={handleMarkerClick}
        userLocation={userLocation}
      />
      {isLoading && (
        <div className="map-loading">
          <LoadingSpinner />
        </div>
      )}
      <WeatherToggleButton />
      <CurrentLocationButton onClick={requestLocation} />
      {hasFetched && !isLoading && trucks.length === 0 && !selectedTruck && (
        <NoTrucksNearby center={center} />
      )}
      {!selectedTruck && (
        <PersonalRecommendation
          lat={userLocation?.lat ?? null}
          lng={userLocation?.lng ?? null}
          onSelectTruck={setSelectedTruck}
        />
      )}
      {selectedTruck && (
        <FoodTruckBottomSheet
          truck={selectedTruck}
          onClose={() => setSelectedTruck(null)}
        />
      )}

    </div>
  );
};

export default MainMapPage;
