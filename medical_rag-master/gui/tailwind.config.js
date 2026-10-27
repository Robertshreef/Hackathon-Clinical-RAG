/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: "#0F1B3D",
          50: "#F1F3FA",
          100: "#D6DBEE",
          200: "#AAB4D6",
          400: "#4A5B8C",
          600: "#1E2E63",
          700: "#16234F",
          800: "#0F1B3D",
          900: "#0B1330",
          950: "#070C22",
        },
        brand: {
          DEFAULT: "#2F6FED",
          50: "#EEF3FF",
          100: "#DCE7FF",
          400: "#5C8FF2",
          600: "#2F6FED",
          700: "#2557C7",
        },
        teal: {
          DEFAULT: "#0EA5A0",
          soft: "#CFF3F1",
          dim: "#0B7D79",
        },
        mist: {
          DEFAULT: "#F5F8FC",
          dim: "#EAF0F8",
          line: "#DCE5F2",
        },
        mint: {
          DEFAULT: "#1E9E6B",
        },
        rose: {
          DEFAULT: "#D64545",
        },
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'Inter'", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(15,27,61,0.05), 0 6px 18px rgba(15,27,61,0.06)",
        rail: "-8px 0 24px rgba(15,27,61,0.05)",
        glow: "0 0 0 4px rgba(47,111,237,0.12)",
      },
    },
  },
  plugins: [],
};
