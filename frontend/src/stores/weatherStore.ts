import { create } from 'zustand';

const RAIN_CODES = new Set([
  51, 53, 55, 56, 57,
  61, 63, 65, 66, 67,
  80, 81, 82,
  95, 96, 99,
]);

interface WeatherState {
  isRaining: boolean;
  checked: boolean;
  setRaining: (v: boolean) => void;
  checkWeather: (lat: number, lng: number) => Promise<void>;
}

export const useWeatherStore = create<WeatherState>((set) => ({
  isRaining: false,
  checked: false,
  setRaining: (v) => set({ isRaining: v, checked: true }),
  checkWeather: async (lat, lng) => {
    try {
      const res = await fetch(
        `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lng}&current=weather_code&timezone=auto`
      );
      const data = await res.json();
      const code: number = data.current?.weather_code ?? 0;
      set({ isRaining: RAIN_CODES.has(code), checked: true });
    } catch {
      set({ checked: true });
    }
  },
}));
