/** @type {import('next').NextConfig} */
const nextConfig = {
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