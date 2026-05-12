import { useEffect, useRef, useState } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { recommendationApi, type Recommendation } from '../../services/recommendationApi';
import { truckApi } from '../../services/truckApi';
import type { FoodTruck } from '../../types/truck';

interface Props {
  lat: number | null;
  lng: number | null;
  onSelectTruck: (truck: FoodTruck) => void;
}

export const PersonalRecommendation = ({ lat, lng, onSelectTruck }: Props) => {
  const { user } = useAuthStore();
  const [rec, setRec] = useState<Recommendation | null>(null);
  const [dismissed, setDismissed] = useState(false);
  const hasFetched = useRef(false);

  useEffect(() => {
    if (!user || user.role !== 'customer' || !lat || !lng || hasFetched.current) return;
    hasFetched.current = true;
    recommendationApi.get(lat, lng)
      .then(({ data }) => { if (data) setRec(data); })
      .catch(() => {});
  }, [user, lat, lng]);

  if (!rec || dismissed) return null;

  const handleClick = async () => {
    try {
      const { data } = await truckApi.get(rec.truck_id);
      onSelectTruck(data);
      setDismissed(true);
    } catch {}
  };

  return (
    <div className="personal-rec">
      <button className="personal-rec__close" onClick={() => setDismissed(true)} aria-label="닫기">✕</button>
      <div className="personal-rec__body" onClick={handleClick}>
        <p className="personal-rec__msg">
          당신이 좋아할 만한 <strong>{rec.food_type}</strong> 트럭이{' '}
          <strong>
            {rec.distance_m >= 1000
              ? `${(rec.distance_m / 1000).toFixed(1)}km`
              : `${rec.distance_m}m`}
          </strong> 거리에 있어요!
        </p>
        <p className="personal-rec__name">👉 {rec.truck_name}</p>
      </div>
    </div>
  );
};
