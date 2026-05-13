import { useLocationStore } from '../../stores/locationStore';

interface Props {
  onClick: () => void;
}

export const CurrentLocationButton = ({ onClick }: Props) => {
  const { isLocating } = useLocationStore();
  return (
    <button
      className={`current-location-btn${isLocating ? ' current-location-btn--loading' : ''}`}
      onClick={onClick}
      aria-label="현재 위치로 이동"
      disabled={isLocating}
    >
      {isLocating ? '⏳' : '📍'}
    </button>
  );
};
