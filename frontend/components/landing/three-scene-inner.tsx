'use client';

import { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Sphere, MeshDistortMaterial, Torus, Icosahedron, OrbitControls } from '@react-three/drei';
import * as THREE from 'three';

/* ─── Floating geometric shape ─── */
function FloatingShape({
  position,
  rotation,
  scale,
  speed,
  type,
  color,
}: {
  position: [number, number, number];
  rotation: [number, number, number];
  scale: number;
  speed: number;
  type: 'icosahedron' | 'torus' | 'octahedron';
  color: string;
}) {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((_, delta) => {
    if (!meshRef.current) return;
    meshRef.current.rotation.x += delta * speed * 0.4;
    meshRef.current.rotation.y += delta * speed * 0.6;
  });

  const material = (
    <meshStandardMaterial
      color={color}
      emissive={color}
      emissiveIntensity={0.4}
      metalness={0.8}
      roughness={0.15}
      transparent
      opacity={0.35}
      wireframe={false}
    />
  );

  return (
    <Float speed={1.5} rotationIntensity={0.4} floatIntensity={1.2}>
      <mesh ref={meshRef} position={position} rotation={rotation} scale={scale}>
        {type === 'icosahedron' && <icosahedronGeometry args={[1, 1]} />}
        {type === 'torus' && <torusGeometry args={[1, 0.35, 16, 48]} />}
        {type === 'octahedron' && <octahedronGeometry args={[1, 0]} />}
        {material}
      </mesh>
    </Float>
  );
}

/* ─── Wireframe shape overlay ─── */
function WireframeShape({
  position,
  scale,
  speed,
  type,
}: {
  position: [number, number, number];
  scale: number;
  speed: number;
  type: 'icosahedron' | 'torus' | 'octahedron';
}) {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((_, delta) => {
    if (!meshRef.current) return;
    meshRef.current.rotation.x += delta * speed * 0.3;
    meshRef.current.rotation.y += delta * speed * 0.5;
    meshRef.current.rotation.z += delta * speed * 0.1;
  });

  return (
    <Float speed={1} rotationIntensity={0.3} floatIntensity={0.8}>
      <mesh ref={meshRef} position={position} scale={scale}>
        {type === 'icosahedron' && <icosahedronGeometry args={[1, 1]} />}
        {type === 'torus' && <torusGeometry args={[1, 0.3, 12, 36]} />}
        {type === 'octahedron' && <octahedronGeometry args={[1, 0]} />}
        <meshStandardMaterial
          color="#6366f1"
          emissive="#4338ca"
          emissiveIntensity={0.6}
          metalness={0.9}
          roughness={0.1}
          transparent
          opacity={0.12}
          wireframe
        />
      </mesh>
    </Float>
  );
}

/* ─── Particle field ─── */
function ParticleField({ count = 600 }: { count?: number }) {
  const pointsRef = useRef<THREE.Points>(null);

  const { positions, colors } = useMemo(() => {
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    const palette = [
      new THREE.Color('#6366f1'),
      new THREE.Color('#a855f7'),
      new THREE.Color('#06b6d4'),
      new THREE.Color('#818cf8'),
    ];

    for (let i = 0; i < count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 28;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 18;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 10;

      const c = palette[Math.floor(Math.random() * palette.length)];
      colors[i * 3] = c.r;
      colors[i * 3 + 1] = c.g;
      colors[i * 3 + 2] = c.b;
    }
    return { positions, colors };
  }, [count]);

  useFrame((state) => {
    if (!pointsRef.current) return;
    pointsRef.current.rotation.y = state.clock.getElapsedTime() * 0.025;
    pointsRef.current.rotation.x = Math.sin(state.clock.getElapsedTime() * 0.015) * 0.08;
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          array={positions}
          count={count}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          array={colors}
          count={count}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.055}
        vertexColors
        transparent
        opacity={0.65}
        sizeAttenuation
      />
    </points>
  );
}

/* ─── Large distorted sphere ─── */
function GlowSphere() {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (!meshRef.current) return;
    meshRef.current.rotation.y = clock.getElapsedTime() * 0.08;
    meshRef.current.rotation.z = clock.getElapsedTime() * 0.04;
  });

  return (
    <mesh ref={meshRef} position={[5, -1, -6]} scale={4.5}>
      <sphereGeometry args={[1, 64, 64]} />
      <MeshDistortMaterial
        color="#312e81"
        emissive="#4338ca"
        emissiveIntensity={0.3}
        metalness={0.9}
        roughness={0.2}
        distort={0.3}
        speed={1.5}
        transparent
        opacity={0.18}
      />
    </mesh>
  );
}

/* ─── Neural network node rings ─── */
function RingGroup() {
  const groupRef = useRef<THREE.Group>(null);
  useFrame(({ clock }) => {
    if (!groupRef.current) return;
    groupRef.current.rotation.x = clock.getElapsedTime() * 0.06;
    groupRef.current.rotation.y = clock.getElapsedTime() * 0.1;
  });

  return (
    <group ref={groupRef} position={[-7, 2, -3]}>
      {[1.2, 2, 2.8].map((r, i) => (
        <mesh key={r} rotation={[Math.PI / 2 + i * 0.4, 0, i * 0.6]}>
          <torusGeometry args={[r, 0.02, 8, 80]} />
          <meshStandardMaterial
            color="#a855f7"
            emissive="#7c3aed"
            emissiveIntensity={1}
            transparent
            opacity={0.3 - i * 0.06}
          />
        </mesh>
      ))}
    </group>
  );
}

/* ─── Scene ─── */
function Scene() {
  const shapes = [
    { position: [-8, 3, -2] as [number, number, number], rotation: [0.5, 0.3, 0] as [number, number, number], scale: 1.4, speed: 0.4, type: 'icosahedron' as const, color: '#6366f1' },
    { position: [8, -2, -3] as [number, number, number], rotation: [1, 0, 0.5] as [number, number, number], scale: 1.1, speed: 0.3, type: 'torus' as const, color: '#a855f7' },
    { position: [-6, -3, -4] as [number, number, number], rotation: [0, 1, 0] as [number, number, number], scale: 0.9, speed: 0.5, type: 'octahedron' as const, color: '#06b6d4' },
    { position: [6, 4, -5] as [number, number, number], rotation: [0.3, 0.6, 0] as [number, number, number], scale: 1.6, speed: 0.25, type: 'icosahedron' as const, color: '#818cf8' },
    { position: [0, -4, -6] as [number, number, number], rotation: [0, 0, 1] as [number, number, number], scale: 1.0, speed: 0.35, type: 'torus' as const, color: '#7c3aed' },
    { position: [-3, 5, -3] as [number, number, number], rotation: [1, 0.3, 0.5] as [number, number, number], scale: 0.7, speed: 0.6, type: 'octahedron' as const, color: '#22d3ee' },
  ];

  const wireShapes = [
    { position: [-4, 1, -7] as [number, number, number], scale: 3.5, speed: 0.1, type: 'icosahedron' as const },
    { position: [9, -4, -8] as [number, number, number], scale: 3, speed: 0.08, type: 'torus' as const },
  ];

  return (
    <>
      <ambientLight intensity={0.15} />
      <pointLight position={[10, 10, 10]} intensity={1.5} color="#6366f1" />
      <pointLight position={[-10, -10, -5]} intensity={1} color="#a855f7" />
      <pointLight position={[0, 5, 5]} intensity={0.5} color="#06b6d4" />

      <ParticleField count={700} />
      <GlowSphere />
      <RingGroup />

      {shapes.map((s, i) => (
        <FloatingShape key={i} {...s} />
      ))}
      {wireShapes.map((s, i) => (
        <WireframeShape key={i} {...s} />
      ))}
    </>
  );
}

/* ─── Export ─── */
export function ThreeSceneInner() {
  return (
    <div className="absolute inset-0 pointer-events-none" style={{ zIndex: 0 }}>
      <Canvas
        camera={{ position: [0, 0, 12], fov: 60 }}
        gl={{ alpha: true, antialias: true }}
        style={{ background: 'transparent' }}
      >
        <Scene />
      </Canvas>
    </div>
  );
}
