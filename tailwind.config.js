/** @type {import('tailwindcss').Config} */

/** Changes this file require the Docker image to be rebuild to take effect **/

module.exports = {
  content: [
    '/srv/templates/**/*.html',
    '/front/node_modules/flowbite/**/*.js',
    './src/project/templates/**/*.html',
    './src/project/templates/components/*.html'
  ],
  darkMode: 'class',
  theme: {
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
