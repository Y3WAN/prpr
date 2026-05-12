const DROPS = Array.from({ length: 90 }, (_, i) => ({
  left: `${((i / 90) * 120) - 10}%`,
  delay: `-${((i * 0.022) % 1.8).toFixed(2)}s`,
  duration: `${0.6 + (i % 8) * 0.06}s`,
  height: `${13 + (i % 10) * 3}px`,
  opacity: String((0.28 + (i % 6) * 0.07).toFixed(2)),
}));

export const RainOverlay = () => (
  <div className="rain-overlay" aria-hidden="true">
    {DROPS.map((d, i) => (
      <span
        key={i}
        className="rain-drop"
        style={{
          left: d.left,
          animationDelay: d.delay,
          animationDuration: d.duration,
          height: d.height,
          opacity: d.opacity,
        }}
      />
    ))}
  </div>
);
