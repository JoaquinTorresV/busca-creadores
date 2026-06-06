import type { Config } from "tailwindcss";

// Tema oscuro/moody, estética profesional.
const config: Config = {
  content: [
    "./src/app/**/*.{ts,tsx}",
    "./src/components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#0a0a0c",
        surface: "#141418",
        surface2: "#1c1c22",
        border: "#2a2a32",
        accent: "#6366f1",
        accentHover: "#7c7ff5",
        muted: "#8b8b96",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
