import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  output: 'standalone',
  // Disable static optimization since this is a fully client-side app
  experimental: {
    // @ts-ignore - this is a valid option
    isrMemoryCacheSize: 0,
  },
};

export default nextConfig;
