import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#111827",
        muted: "#6B7280",
        line: "#D7DEE8",
        panel: "#F7F9FC",
        brand: "#1F6FEB",
        success: "#11845B",
        warning: "#B7791F",
        danger: "#B42318"
      },
      boxShadow: {
        soft: "0 12px 30px rgba(17, 24, 39, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;
