import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// In dev (port 5175), proxy the backend API paths to FastAPI on :8000 so the
// frontend can use same-origin relative URLs in both dev and production.
const API_PATHS = ["/report", "/graph", "/rings", "/package", "/health",
  "/alerts", "/geo", "/currency", "/call", "/analytics", "/languages",
  "/impact", "/events"];

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5175,
    proxy: Object.fromEntries(
      API_PATHS.map((p) => [p, { target: "http://localhost:8000", changeOrigin: true }])
    ),
  },
});
