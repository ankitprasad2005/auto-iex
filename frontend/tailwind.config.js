export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        nd: {
          black: "#000000",
          surface: "#111111",
          "surface-raised": "#1A1A1A",
          border: "#222222",
          "border-visible": "#333333",
          "text-disabled": "#666666",
          "text-secondary": "#999999",
          "text-primary": "#E8E8E8",
          "text-display": "#FFFFFF",
          accent: "#D71921",
          "accent-subtle": "rgba(215,25,33,0.15)",
          success: "#4A9E5C",
          warning: "#D4A843",
          interactive: "#5B9BF6",
        },
      },
      fontFamily: {
        display: ["Doto", "Space Mono", "monospace"],
        body: ["Space Grotesk", "DM Sans", "system-ui", "sans-serif"],
        mono: ["Space Mono", "JetBrains Mono", "monospace"],
      },
      letterSpacing: {
        label: "0.08em",
      },
    },
  },
  plugins: [],
};
