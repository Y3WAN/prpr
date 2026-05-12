import api from './api';
import type { Review, MyReview } from '../types/review';

export const reviewApi = {
  list: (truckId: number) => api.get<Review[]>(`/trucks/${truckId}/reviews`),

  create: (truckId: number, data: { content: string; rating: number }) =>
    api.post<Review>(`/trucks/${truckId}/reviews`, data),

  update: (reviewId: number, data: { content: string; rating: number }) =>
    api.put<Review>(`/reviews/${reviewId}`, data),

  delete: (reviewId: number) => api.delete(`/reviews/${reviewId}`),

  myReviews: () => api.get<MyReview[]>('/my/reviews'),
};
