import type { Review } from '../../types/review';
import { ReviewItem } from './ReviewItem';
import { ReviewForm } from './ReviewForm';

interface Props {
  reviews: Review[];
  truckId: number;
  canWrite: boolean;
  onReviewChanged: () => void;
}

export const ReviewSection = ({ reviews, truckId, canWrite, onReviewChanged }: Props) => (
  <div className="review-section">
    <h3 className="section-title">리뷰 ({reviews.length})</h3>
    {canWrite && <ReviewForm truckId={truckId} onSubmitted={onReviewChanged} />}
    <div className="review-list">
      {reviews.length === 0 ? (
        <p className="empty-message">아직 리뷰가 없습니다.</p>
      ) : (
        reviews.map((r) => <ReviewItem key={r.id} review={r} onChanged={onReviewChanged} />)
      )}
    </div>
  </div>
);
