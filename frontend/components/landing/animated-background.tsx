'use client';

import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { ThreeScene } from './three-scene';

export function AnimatedBackground() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden bg-[#030306]">
      {/* 3D Three.js scene */}
      <ThreeScene />

      {/* 2D canvas neural network overlay */}
      <NeuralCanvas />

      {/* Colour orbs */}
      <FloatingOrbs />

      {/* Dot-grid */}
      <GridOverlay />

      {/* Fade-out bottom */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-[#030306]/70 pointer-events-none" />
    </div>
  );
}

/* ─── Canvas neural network (2D lines + dots) ─── */
function NeuralCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    const count = Math.max(35, Math.floor((window.innerWidth * window.innerHeight) / 22000));
    const nodes = Array.from({ length: count }, () => ({
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      vx: (Math.random() - 0.5) * 0.2,
      vy: (Math.random() - 0.5) * 0.2,
      r: Math.random() * 1.5 + 0.5,
      pulse: Math.random() * Math.PI * 2,
    }));

    let id: number;
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      nodes.forEach((n) => {
        n.x += n.vx;
        n.y += n.vy;
        n.pulse += 0.02;
        if (n.x < 0 || n.x > canvas.width) n.vx *= -1;
        if (n.y < 0 || n.y > canvas.height) n.vy *= -1;
      });

      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 160) {
            const alpha = (1 - dist / 160) * 0.12;
            ctx.beginPath();
            ctx.strokeStyle = `rgba(99,102,241,${alpha})`;
            ctx.lineWidth = 0.4;
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);
            ctx.stroke();
          }
        }
      }

      nodes.forEach((n) => {
        const glow = 0.3 + Math.sin(n.pulse) * 0.2;
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r * (0.9 + Math.sin(n.pulse) * 0.2), 0, Math.PI * 2);
        ctx.fillStyle = `rgba(139,92,246,${glow})`;
        ctx.fill();
      });

      id = requestAnimationFrame(draw);
    };
    draw();

    return () => {
      cancelAnimationFrame(id);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full opacity-40"
    />
  );
}

/* ─── Soft colour orbs ─── */
function FloatingOrbs() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      <motion.div
        className="absolute top-[8%] left-[12%] w-[560px] h-[560px] rounded-full"
        style={{ background: 'radial-gradient(circle, rgba(99,102,241,0.11) 0%, transparent 65%)' }}
        animate={{ x: [0, 70, 0], y: [0, -30, 0] }}
        transition={{ duration: 24, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="absolute top-[38%] right-[8%] w-[440px] h-[440px] rounded-full"
        style={{ background: 'radial-gradient(circle, rgba(168,85,247,0.10) 0%, transparent 65%)' }}
        animate={{ x: [0, -50, 0], y: [0, 55, 0] }}
        transition={{ duration: 30, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="absolute bottom-[12%] left-[32%] w-[380px] h-[380px] rounded-full"
        style={{ background: 'radial-gradient(circle, rgba(6,182,212,0.08) 0%, transparent 65%)' }}
        animate={{ x: [0, 40, 0], y: [0, -45, 0] }}
        transition={{ duration: 20, repeat: Infinity, ease: 'easeInOut' }}
      />
    </div>
  );
}

/* ─── Dot-grid overlay ─── */
function GridOverlay() {
  return (
    <div
      className="absolute inset-0 opacity-[0.25]"
      style={{
        backgroundImage: 'radial-gradient(rgba(99,102,241,0.28) 1px, transparent 1px)',
        backgroundSize: '48px 48px',
      }}
    />
  );
}

/* ─── Re-exported for usage in non-fixed contexts ─── */
export function Particles() {
  return null;
}
