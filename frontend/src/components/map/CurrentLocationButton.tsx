interface Props {
  onClick: () => void;
}

export const CurrentLocationButton = ({ onClick }: Props) => (
  <button className="current-location-btn" onClick={onClick} aria-label="현재 위치로 이동">
    📍
  </button>
);
