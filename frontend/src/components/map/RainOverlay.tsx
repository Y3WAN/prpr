import { useEffect, useRef } from 'react';

interface Drop {
  x: number;
  y: number;
  len: number;
  speed: number;
  opacity: number;
}

export const RainOverlay = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    const drops: Drop[] = Array.from({ length: 200 }, () => ({
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      len: Math.random() * 22 + 12,
      speed: Math.random() * 9 + 10,
      opacity: Math.random() * 0.35 + 0.35,
    }));

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      drops.forEach((d) => {
        const dx = -d.speed * 0.22;
        const dy = d.speed;

        ctx.save();
        ctx.globalAlpha = d.opacity;
        ctx.strokeStyle = 'rgba(180, 220, 255, 1)';
        ctx.lineWidth = 1.5;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(d.x, d.y);
        ctx.lineTo(d.x + dx * (d.len / d.speed), d.y + d.len);
        ctx.stroke();
        ctx.restore();

        d.x += dx;
        d.y += dy;

        if (d.y > canvas.height + d.len) {
          d.y = -d.len - Math.random() * 100;
          d.x = Math.random() * (canvas.width + 150);
        }
        if (d.x < -100) {
          d.x = canvas.width + Math.random() * 50;
          d.y = Math.random() * canvas.height;
        }
      });

      animId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 45,
      }}
    />
  );
};
