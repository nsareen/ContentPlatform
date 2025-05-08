/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      fontFamily: {
        sans: ['var(--font-inter)', 'var(--font-roboto)', 'sans-serif'],
        equip: ['Equip', 'var(--font-roboto)', 'sans-serif'],
      },
      colors: {
        // Design system colors
        primary: {
          DEFAULT: "#6D3BEB", // Primary.Purple
          light: "#8B63F9",   // Primary.PurpleLight
          dark: "#5A26B8",    // Primary.PurpleDark
          foreground: "#FFFFFF",
        },
        secondary: {
          DEFAULT: "#007AFF", // Secondary.Blue
          light: "#3EAFFF",   // Secondary.BlueLight
          foreground: "#FFFFFF",
        },
        text: {
          primary: "#1E2334",   // Text.Primary
          secondary: "#475569", // Text.Secondary
          tertiary: "#94A3B8",  // Text.Tertiary
        },
        background: {
          DEFAULT: "#FFFFFF",  // Background.Default
          surface: "#F8FAFC",  // Background.Surface
          light: "#FFFFFF",    // Background.Light
        },
        border: {
          DEFAULT: "#E2E8F0", // Border.Default
          light: "#F1F5F9",   // Border.Light
        },
        feedback: {
          success: "#10B981", // Feedback.Success
          warning: "#F59E0B", // Feedback.Warning
          error: "#EF4444",   // Feedback.Error
        },
        // Keep shadcn compatibility
        border: "#E2E8F0",
        input: "#E2E8F0",
        ring: "#6D3BEB",
        background: "#FFFFFF",
        foreground: "#1E2334",
        muted: {
          DEFAULT: "#F1F5F9",
          foreground: "#64748B",
        },
        accent: {
          DEFAULT: "#F8FAFC",
          foreground: "#0F172A",
        },
        popover: {
          DEFAULT: "#FFFFFF",
          foreground: "#1E2334",
        },
        card: {
          DEFAULT: "#FFFFFF",
          foreground: "#1E2334",
        },
        destructive: {
          DEFAULT: "#EF4444",
          foreground: "#FFFFFF",
        },
      },
      borderRadius: {
        sm: "4px",  // radius.sm
        md: "8px",  // radius.md
        lg: "16px", // radius.lg
      },
      boxShadow: {
        sm: "0px 1px 2px rgba(0, 0, 0, 0.05)",    // shadow.sm
        md: "0px 4px 8px rgba(0, 0, 0, 0.10)",    // shadow.md
        lg: "0px 8px 16px rgba(0, 0, 0, 0.15)",   // shadow.lg
      },
      spacing: {
        xs: "4px",   // XSmall
        sm: "8px",   // Small
        md: "16px",  // Medium
        lg: "24px",  // Large
        xl: "32px",  // XL
        xxl: "40px", // XXL
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
