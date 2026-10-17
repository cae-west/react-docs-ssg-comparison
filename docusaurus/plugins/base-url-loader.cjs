// Webpack loader: prefixes root-absolute '/images/...' strings in the copied
// react.dev homepage code with the site's base URL (DOCS_BASE_URL), so the
// images also load when the site is served from a subfolder (GitHub Pages).
// With the default base '/', the code is left unchanged.
module.exports = function baseUrlLoader(source) {
  const base = (process.env.DOCS_BASE_URL || '/').replace(/\/?$/, '/');
  if (base === '/') return source;
  return source.replace(/(['"`])\/images\//g, (_, q) => q + base + 'images/');
};
