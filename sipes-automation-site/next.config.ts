import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  async redirects() {
    return [
      {
        source: "/lead-gen",
        destination: "/tools/lead-gen",
        permanent: true,
      },
      // Capture query params as well
      {
        source: "/lead-gen/:slug*",
        destination: "/tools/lead-gen/:slug*",
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
