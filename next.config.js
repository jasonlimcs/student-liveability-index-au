/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  async rewrites() {
    return [
      {
        source: '/maps/:path*',
        destination: '/api/maps/:path*',
      },
    ];
  },
}

module.exports = nextConfig 