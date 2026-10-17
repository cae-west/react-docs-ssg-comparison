// Lets Docusaurus run the original react.dev homepage code: Tailwind CSS (with
// react.dev's own config), plus aliases for the Next.js modules it imports.
const path = require('path');
module.exports = function reactHome() {
  return {
    name: 'react-home',
    configurePostCss(opts) {
      opts.plugins.push(require('tailwindcss')(path.resolve(__dirname, '../src/tailwind.config.js')));
      return opts;
    },
    configureWebpack() {
      return {
        module: {
          rules: [
            {
              test: /react-home[\\/]components[\\/]Layout[\\/]HomeContent\.js$/,
              enforce: 'pre',
              use: [{loader: path.resolve(__dirname, 'base-url-loader.cjs')}],
            },
          ],
        },
        resolve: {
          alias: {
            'next/link': path.resolve(__dirname, '../src/react-home/shims/next-link.js'),
            'next/image': path.resolve(__dirname, '../src/react-home/shims/next-image.js'),
            components: path.resolve(__dirname, '../src/react-home/components'),
          },
        },
      };
    },
  };
};
