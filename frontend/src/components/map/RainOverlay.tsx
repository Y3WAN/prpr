// Deterministic pseudo-random based on index to avoid re-render flicker
const r = (i: number, seed: number, range: number) => ((i * seed + 7919) % range);

const DROPS = Array.from({ length: 160 }, (_, i) => ({
  left:     `${r(i, 37, 130) - 10}%`,
  delay:    `-${(r(i, 13, 220) / 100).toFixed(2)}s`,
  duration: `${(0.38 + r(i, 7, 9) * 0.065).toFixed(2)}s`,
  height:   `${16 + r(i, 11, 20) * 2}px`,
  opacity:  `${(0.22 + r(i, 19, 8) * 0.065).toFixed(2)}`,
  width:    `${i % 5 === 0 ? 2 : 1.5}px`,
}));

export const RainOverlay = () => (
  <div className="rain-overlay" aria-hidden="true">
    {DROPS.map((d, i) => (
      <span
        key={i}
        className="rain-drop"
        style={{
          left:              d.left,
          animationDelay:    d.delay,
          animationDuration: d.duration,
          height:            d.height,
          opacity:           d.opacity,
          width:             d.width,
        }}
      />
    ))}
  </div>
);
