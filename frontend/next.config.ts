import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Docker uchun: faqat kerakli fayllardan iborat minimal server chiqadi
  // (.next/standalone). node_modules to'liq nusxalanmaydi.
  output: "standalone",
  images: {
    // Jamoa logotiplari tashqi manbalardan keladi
    remotePatterns: [
      { protocol: "https", hostname: "media.api-sports.io" },
      { protocol: "https", hostname: "upload.wikimedia.org" },
      // TheSportsDB jamoa gerblari
      { protocol: "https", hostname: "r2.thesportsdb.com" },
      { protocol: "https", hostname: "www.thesportsdb.com" },
    ],
  },
};

export default nextConfig;
