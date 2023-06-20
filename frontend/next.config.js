/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: ["images.unsplash.com", "c.tenor.com", "cdn.dribbble.com","img.freepik.com"],
  },
};

module.exports = nextConfig;
