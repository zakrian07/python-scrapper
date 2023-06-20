module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {

      fontFamily: {
        poppins: ["poppins", "sans-serif"],
      },
      keyframes: {
        spinaround: {
          "0%": { transform: "rotate(0.0deg)" },
          "10%": { transform: "rotate(40deg)" },
          "20%": { transform: "rotate(80deg)" },
          "30%": { transform: "rotate(120deg)" },
          "40%": { transform: "rotate(180deg)" },
          "50%": { transform: "rotate(240deg)" },
          "60%": { transform: "rotate(280deg)" },
          "70%": { transform: "rotate(320deg)" },
          "80%": { transform: "rotate(340deg)" },
          "100%": { transform: "rotate(720deg)" },
        },
        reversespinaround: {
          "0%": { transform: "rotate(0.0deg)" },
          "10%": { transform: "rotate(400deg)" },
          "20%": { transform: "rotate(440deg)" },
          "30%": { transform: "rotate(480deg)" },
          "40%": { transform: "rotate(520deg)" },
          "50%": { transform: "rotate(560deg)" },
          "60%": { transform: "rotate(600deg)" },
          "70%": { transform: "rotate(640deg)" },
          "80%": { transform: "rotate(680deg)" },
          "100%": { transform: "rotate(720deg)" },
        },
      },
      animation: {
        "Loader-animation": "spinaround 4s linear infinite",
        "Loader-reverse-animation": "reversespinaround 4s linear infinite",
      },
      colors: {
        'red-500': '#FF0000',
        'odd-color': '#5faba270',
      },
    },
  },
  plugins: [
    // ...
    require("@tailwindcss/forms"),
  ],
};
