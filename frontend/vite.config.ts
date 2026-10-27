import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test-setup.ts"],
    coverage: {
      include: ["src/**"],
      exclude: ["src/**/*.test.*", "src/main.tsx", "src/vite-env.d.ts", "src/test-setup.ts"],
    },
  },
});
