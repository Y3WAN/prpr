import { useEffect, useState } from 'react';
import type { FoodTruck } from '../../types/truck';
import type { Review } from '../../types/review';
import { useAuthStore } from '../../stores/authStore';
import { reviewApi } from '../../services/reviewApi';
import { truckApi } from '../../services/truckApi';
import { TruckInfoSection } from './TruckInfoSection';
import { MenuListSection } from './MenuListSection';
import { ReviewSection } from '../review/ReviewSection';

interface Props {
  truck: FoodTruck;
  onClose: () => void;
}

export const FoodTruckBottomSheet = ({ truck, onClose }: Props) => {
  const { user } = useAuthStore();
  const [reviews, setReviews] = useState<Review[]>([]);
  const [keywords, setKeywords] = useState<string[]>([]);

  const loadReviews = () => {
    reviewApi.list(truck.id).then(({ data }) => setReviews(data));
  };

  useEffect(() => {
    loadReviews();
    truckApi.keywords(truck.id)
      .then(({ data }) => setKeywords(data.keywords))
      .catch(() => {});
  }, [truck.id]);

  return (
    <div className="bottom-sheet-overlay" onClick={onClose}>
      <div className="bottom-sheet" onClick={(e) => e.stopPropagation()}>
        <button className="bottom-sheet__close" onClick={onClose} aria-label="닫기">✕</button>
        <div className="bottom-sheet__content">
          <TruckInfoSection truck={truck} keywords={keywords} />
          <MenuListSection menus={truck.menus} />
          <ReviewSection
            reviews={reviews}
            truckId={truck.id}
            canWrite={user?.role === 'customer'}
            onReviewChanged={loadReviews}
          />
        </div>
      </div>
    </div>
  );
};
