import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    // Jamoa logotiplari tashqi manbalardan keladi
    remotePatterns: [
      { protocol: "https", hostname: "media.api-sports.io" },
      { protocol: "https", hostname: "upload.wikimedia.org" },
    ],
  },
};

export default nextConfig;
