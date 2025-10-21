/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost'],
  },
  // Proxy API requests to backend to avoid mixed content errors (HTTPS -> HTTP)
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://51.112.224.105/api/:path*',
      },
    ];
  },
}

module.exports = nextConfig

