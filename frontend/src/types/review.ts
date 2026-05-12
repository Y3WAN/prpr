export interface Review {
  id: number;
  content: string;
  rating: number;
  created_at: string;
  updated_at: string;
  user: {
    id: number;
    nickname: string;
  };
}

export interface MyReview {
  id: number;
  content: string;
  rating: number;
  truck: {
    id: number;
    name: string;
  };
  created_at: string;
}
