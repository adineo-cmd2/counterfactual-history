/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        parchment: '#faf3e3',
        agedbrown: '#57534e',
        deepred: '#b91c1c',
        mossgreen: '#166534',
      },
    },
  },
  plugins: [],
};
