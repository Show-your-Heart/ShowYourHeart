/** @type {import('tailwindcss').Config} */

/** Changes this file require the Docker image to be rebuild to take effect **/

module.exports = {
  content: [
    '/srv/templates/**/*.html',
    '/front/node_modules/flowbite/**/*.js'
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          "50":"#E1F8F8",
          "100":"#B2EFEF",
          "200":"#7BF3F3",
          "300":"#7BEAEA",
          "400":"#6EDADA",
          "500":"#66CCCC",
          "600":"#56B6B6",
          "700":"#439C9C",
          "800":"#4D9393",
          "900":"#397575",
          "950":"#295252"
        }
      }
    },
    fontFamily: {
      'body': ['Montserrat', 'sans-serif'],
      'sans': ['Montserrat', 'sans-serif']
    }
  },
  plugins: [
    require('flowbite/plugin')
  ],
  safelist: [
    "bg-primary-400", // Required by settings.py:ACTIVE_LINK_CSS_CLASS.
  ]
}
