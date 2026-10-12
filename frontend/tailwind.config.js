/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        mesh: {
          bg: "#060913",
          surface: "#0d1322",
          card: "#121a2f",
          border: "#1e2942",
          accent: "#06b6d4",
          neon: "#22d3ee",
          violet: "#8b5cf6",
          emerald: "#10b981",
          rose: "#f43f5e",
          amber: "#f59e0b"
        }
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'monospace', 'Consolas'],
        sans: ['"Inter"', 'system-ui', 'sans-serif'],
      },
      animation: {
        'pulse-glow': 'pulseGlow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'radar-sweep': 'radarSweep 4s linear infinite',
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { opacity: 1, filter: 'drop-shadow(0 0 12px rgba(6, 182, 212, 0.8))' },
          '50%': { opacity: 0.6, filter: 'drop-shadow(0 0 4px rgba(6, 182, 212, 0.3))' },
        },
        radarSweep: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        }
      }
    },
  },
  plugins: [],
}
