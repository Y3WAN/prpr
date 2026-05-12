interface Props {
  value: number;
  onChange?: (rating: number) => void;
  readonly?: boolean;
}

export const StarRating = ({ value, onChange, readonly = false }: Props) => (
  <div className="star-rating">
    {[1, 2, 3, 4, 5].map((star) => (
      <span
        key={star}
        className={`star ${star <= value ? 'star--filled' : ''} ${!readonly ? 'star--interactive' : ''}`}
        onClick={() => !readonly && onChange?.(star)}
      >
        ★
      </span>
    ))}
  </div>
);
