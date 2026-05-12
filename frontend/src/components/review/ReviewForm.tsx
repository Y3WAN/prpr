import { useState } from 'react';
import { StarRating } from './StarRating';
import { reviewApi } from '../../services/reviewApi';
import { showToast } from '../common/Toast';
import { Button } from '../common/Button';

interface Props {
  truckId: number;
  onSubmitted: () => void;
}

export const ReviewForm = ({ truckId, onSubmitted }: Props) => {
  const [content, setContent] = useState('');
  const [rating, setRating] = useState(5);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) {
      showToast('리뷰 내용을 입력해주세요.', 'warning');
      return;
    }
    setLoading(true);
    try {
      await reviewApi.create(truckId, { content, rating });
      setContent('');
      setRating(5);
      onSubmitted();
      showToast('리뷰가 등록되었습니다.', 'success');
    } catch (err: any) {
      showToast(err.response?.data?.detail ?? '리뷰 등록에 실패했습니다.', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="review-form" onSubmit={handleSubmit}>
      <h4 className="review-form__title">리뷰 작성</h4>
      <StarRating value={rating} onChange={setRating} />
      <textarea
        className="review-textarea"
        placeholder="가게에 대한 리뷰를 남겨주세요."
        value={content}
        onChange={(e) => setContent(e.target.value)}
        rows={3}
      />
      <Button type="submit" disabled={loading} fullWidth>
        {loading ? '등록 중...' : '리뷰 등록'}
      </Button>
    </form>
  );
};
