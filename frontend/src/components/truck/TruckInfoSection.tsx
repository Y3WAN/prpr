import type { FoodTruck } from '../../types/truck';
import { StarRating } from '../review/StarRating';

interface Props {
  truck: FoodTruck;
  keywords?: string[];
}

export const TruckInfoSection = ({ truck, keywords }: Props) => (
  <div className="truck-info">
    {truck.image_url && (
      <img className="truck-info__image" src={truck.image_url} alt={truck.name} />
    )}
    <div className="truck-info__body">
      <div className="truck-info__header">
        <h2 className="truck-info__name">{truck.name}</h2>
        <span className={`truck-info__status ${truck.is_open ? 'truck-info__status--open' : 'truck-info__status--closed'}`}>
          {truck.is_open ? '영업중' : '영업종료'}
        </span>
      </div>
      {keywords && keywords.length > 0 && (
        <div className="truck-info__keywords">
          {keywords.map((kw) => (
            <span key={kw} className="truck-keyword"># {kw}</span>
          ))}
        </div>
      )}
      <div className="truck-info__rating">
        <StarRating value={Math.round(truck.avg_rating)} readonly />
        <span className="truck-info__rating-text">
          {truck.avg_rating.toFixed(1)} ({truck.review_count}개 리뷰)
        </span>
      </div>
      {truck.description && <p className="truck-info__desc">{truck.description}</p>}
      {truck.account_info && (
        <p className="truck-info__account">계좌: {truck.account_info}</p>
      )}
    </div>
  </div>
);
