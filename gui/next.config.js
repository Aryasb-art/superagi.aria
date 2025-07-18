/** @type {import('next').NextConfig} */
const nextConfig = {
  assetPrefix: process.env.NODE_ENV === "production" ? "/" : "./",
  output: 'standalone',
  experimental: {
    esmExternals: false
  },
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }
    
    // Handle echarts for SSR
    if (isServer) {
      config.externals = [...(config.externals || []), 'echarts'];
    }
    
    return config;
  },
  transpilePackages: ['echarts']
};

module.exports = nextConfig;
