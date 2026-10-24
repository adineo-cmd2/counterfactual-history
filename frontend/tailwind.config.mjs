/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        "parchment": "#f8f1dd",
        "agedbrown": "#57534e",
        "deepred": "#a91f1f",
        "mossgreen": "#166534"
},
      fontFamily: {
        "display": [
                "'Cormorant Garamond'",
                "Georgia",
                "serif"
        ],
        "body": [
                "'Inter'",
                "system-ui",
                "sans-serif"
        ],
        "mono": [
                "'JetBrains Mono'",
                "ui-monospace",
                "monospace"
        ]
},
    },
  },
  plugins: [],
};
