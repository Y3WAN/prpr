import type { Review } from '../../types/review';
import { StarRating } from './StarRating';
import { useAuthStore } from '../../stores/authStore';
import { useState } from 'react';
import { reviewApi } from '../../services/reviewApi';
import { showToast } from '../common/Toast';

interface Props {
  review: Review;
  onChanged: () => void;
}

export const ReviewItem = ({ review, onChanged }: Props) => {
  const { user } = useAuthStore();
  const [editing, setEditing] = useState(false);
  const [content, setContent] = useState(review.content);
  const [rating, setRating] = useState(review.rating);

  const isOwner = user?.id === review.user.id;

  const handleUpdate = async () => {
    try {
      await reviewApi.update(review.id, { content, rating });
      setEditing(false);
      onChanged();
      showToast('리뷰가 수정되었습니다.', 'success');
    } catch {
      showToast('수정에 실패했습니다.', 'error');
    }
  };

  const handleDelete = async () => {
    if (!confirm('리뷰를 삭제하시겠습니까?')) return;
    try {
      await reviewApi.delete(review.id);
      onChanged();
      showToast('리뷰가 삭제되었습니다.', 'success');
    } catch {
      showToast('삭제에 실패했습니다.', 'error');
    }
  };

  if (editing) {
    return (
      <div className="review-item review-item--editing">
        <StarRating value={rating} onChange={setRating} />
        <textarea
          className="review-textarea"
          value={content}
          onChange={(e) => setContent(e.target.value)}
        />
        <div className="review-item__actions">
          <button className="btn btn--primary btn--sm" onClick={handleUpdate}>저장</button>
          <button className="btn btn--secondary btn--sm" onClick={() => setEditing(false)}>취소</button>
        </div>
      </div>
    );
  }

  return (
    <div className="review-item">
      <div className="review-item__header">
        <span className="review-item__nickname">{review.user.nickname}</span>
        <StarRating value={review.rating} readonly />
        {isOwner && (
          <div className="review-item__actions">
            <button className="btn--link" onClick={() => setEditing(true)}>수정</button>
            <button className="btn--link btn--link--danger" onClick={handleDelete}>삭제</button>
          </div>
        )}
      </div>
      <p className="review-item__content">{review.content}</p>
      <span className="review-item__date">{new Date(review.created_at).toLocaleDateString()}</span>
    </div>
  );
};
