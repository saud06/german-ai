/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  experimental: {
    // Improves startup and treeshaking for frequently used libs
    optimizePackageImports: [
      'react',
      'react-dom',
      'next',
      'clsx',
      'zustand',
    ],
  },
  webpack: (config, { dev }) => {
    // Use proper source maps in dev to avoid eval-wrapped bundles that
    // sometimes trigger browser parsing quirks
    if (dev) {
      config.devtool = 'source-map';
    }
    return config;
  },
};
export default nextConfig;
