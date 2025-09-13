import type { NextConfig } from "next";
import path from 'path';

const nextConfig: NextConfig = {
  // Ensure proper module resolution
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname, 'src'),
      '@/lib': path.resolve(__dirname, 'src/lib'),
      '@/components': path.resolve(__dirname, 'src/components'),
      '@/contexts': path.resolve(__dirname, 'src/contexts'),
      '@/types': path.resolve(__dirname, 'src/types'),
    };
    return config;
  },
};

export default nextConfig;
