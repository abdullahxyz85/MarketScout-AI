'use client';

import dynamic from 'next/dynamic';

export const ThreeScene = dynamic(
  () => import('./three-scene-inner').then((m) => m.ThreeSceneInner),
  { ssr: false, loading: () => null }
);
