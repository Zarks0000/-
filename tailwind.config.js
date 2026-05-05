/** @type {import('tailwindcss').Config} */

export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,vue,json}"],
  theme: {
    container: {
      center: true,
    },
    extend: {},
  },
  plugins: [],
  corePlugins: {
    preflight: false,
  },
};
