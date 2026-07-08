/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  images: { unoptimized: true },
<<<<<<< HEAD
=======
  async rewrites() {
    // These rewrites are used in local development (npm run dev).
    // In production, nginx handles all routing.
    // /api/agents/* → agent-service on port 8001
    // /api/*        → backend on port 8000
    return [
      {
        source: '/api/agents/:path*',
        destination: 'http://localhost:8001/:path*',
      },
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
>>>>>>> add-ai-agent-service
};

module.exports = nextConfig;
