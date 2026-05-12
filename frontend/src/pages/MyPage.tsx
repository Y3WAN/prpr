import { useEffect, useState } from 'react';
import { useAuthStore } from '../stores/authStore';
import { reviewApi } from '../services/reviewApi';
import type { MyReview } from '../types/review';
import { StarRating } from '../components/review/StarRating';
import { showToast } from '../components/common/Toast';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

const MyPage = () => {
  const { user } = useAuthStore();
  const [reviews, setReviews] = useState<MyReview[]>([]);
  const [loading, setLoading] = useState(true);

  const loadReviews = async () => {
    try {
      const { data } = await reviewApi.myReviews();
      setReviews(data);
    } catch {
      showToast('리뷰를 불러오지 못했습니다.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReviews();
  }, []);

  const handleDelete = async (id: number) => {
    if (!confirm('리뷰를 삭제하시겠습니까?')) return;
    try {
      await reviewApi.delete(id);
      setReviews((prev) => prev.filter((r) => r.id !== id));
      showToast('삭제되었습니다.', 'success');
    } catch {
      showToast('삭제에 실패했습니다.', 'error');
    }
  };

  return (
    <div className="my-page">
      <div className="my-page__header">
        <h2>내 정보</h2>
        <div className="my-page__user-info">
          <p><strong>닉네임:</strong> {user?.nickname}</p>
          <p><strong>이메일:</strong> {user?.email}</p>
          <p><strong>역할:</strong> {user?.role === 'owner' ? '사장님' : '손님'}</p>
        </div>
      </div>

      <section className="my-page__reviews">
        <h3>내가 쓴 리뷰 ({reviews.length})</h3>
        {loading ? (
          <LoadingSpinner />
        ) : reviews.length === 0 ? (
          <p className="empty-message">작성한 리뷰가 없습니다.</p>
        ) : (
          <ul className="my-review-list">
            {reviews.map((r) => (
              <li key={r.id} className="my-review-item">
                <div className="my-review-item__header">
                  <strong>{r.truck.name}</strong>
                  <StarRating value={r.rating} readonly />
                </div>
                <p>{r.content}</p>
                <div className="my-review-item__footer">
                  <span>{new Date(r.created_at).toLocaleDateString()}</span>
                  <button className="btn--link btn--link--danger" onClick={() => handleDelete(r.id)}>삭제</button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
};

export default MyPage;
