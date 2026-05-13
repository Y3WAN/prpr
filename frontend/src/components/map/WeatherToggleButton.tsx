import { useWeatherStore } from '../../stores/weatherStore';

export const WeatherToggleButton = () => {
  const { isRaining, setRaining } = useWeatherStore();

  return (
    <button
      className="weather-toggle-btn"
      onClick={() => setRaining(!isRaining)}
      aria-label={isRaining ? '맑은 화면으로 전환' : '비 오는 화면으로 전환'}
      title={isRaining ? '맑음으로 전환' : '비 UI로 전환'}
    >
      {isRaining ? '☀️' : '🌧️'}
    </button>
  );
};
