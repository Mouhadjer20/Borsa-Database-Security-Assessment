/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Dark backgrounds — navy/slate spectrum
        'bg-primary':   '#030712', // gray-950
        'bg-secondary': '#111827', // gray-900
        'bg-card':      '#1f2937', // gray-800
        'bg-elevated':  '#374151', // gray-700

        // Accent — gold/amber for Borsa branding & primary actions
        'accent': {
          DEFAULT: '#f59e0b', // amber-500
          light:   '#fbbf24', // amber-400
          dark:    '#d97706', // amber-600
        },

        // Financial status colors
        'positive': '#22c55e', // green-500
        'negative': '#ef4444', // red-500
        'pending':  '#f59e0b', // amber-500
        'neutral':  '#6b7280', // gray-500

        // Security lab — warning palette
        'lab': {
          bg:     '#1c1507', // very dark amber tint
          border: '#92400e', // amber-800
          accent: '#fbbf24', // amber-400
          danger: '#dc2626', // red-600
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      },
      boxShadow: {
        'card':    '0 1px 3px rgba(0,0,0,0.5), 0 1px 2px rgba(0,0,0,0.3)',
        'card-lg': '0 4px 6px rgba(0,0,0,0.5), 0 2px 4px rgba(0,0,0,0.3)',
        'glow-amber': '0 0 12px rgba(245,158,11,0.25)',
        'glow-red':   '0 0 12px rgba(239,68,68,0.25)',
      },
      animation: {
        'fade-in':    'fadeIn 0.2s ease-in-out',
        'slide-in':   'slideIn 0.2s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { opacity: '0', transform: 'translateY(-8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
};
