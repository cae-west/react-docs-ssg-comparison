// Docusaurus-side adapter for react.dev conventions. Runs while the pages are
// compiled, so the content files themselves are never changed.
//  1. Images written as ../images/x.png work on react.dev (the browser resolves
//     them from the page URL) but Docusaurus resolves them from the file's folder.
//     Point them at /images/x.png, where the copied images are served.
//  2. Raw <img src="/images/..."> and <source srcset> tags in the content are root-absolute, so they
//     break when the site is served from a subfolder (GitHub Pages). Prefix them
//     with the base URL (DOCS_BASE_URL, same variable docusaurus.config.js uses).
//  3. react.dev headings carry explicit anchor ids as  ## Usage {/*usage*/}.
//     Docusaurus doesn't read that syntax, so apply the id to the heading.
export default function reactDocsRemark() {
  return (tree) => walk(tree);
}

const BASE = (process.env.DOCS_BASE_URL || '/').replace(/\/?$/, '/');

function walk(node) {
  if ((node.type === 'mdxJsxFlowElement' || node.type === 'mdxJsxTextElement') && Array.isArray(node.attributes)) {
    // <img src="/images/..."> and <source srcset="/images/..."> (inside <picture>)
    const wanted = node.name === 'img' ? ['src'] : node.name === 'source' ? ['srcset', 'srcSet'] : [];
    for (const attr of node.attributes) {
      if (attr.type === 'mdxJsxAttribute' && wanted.includes(attr.name) && typeof attr.value === 'string'
          && attr.value.startsWith('/') && !attr.value.startsWith('//') && BASE !== '/' && !attr.value.startsWith(BASE)) {
        attr.value = BASE + attr.value.slice(1);
      }
    }
  }
  if (node.type === 'image' && typeof node.url === 'string' && node.url.startsWith('../images/')) {
    node.url = node.url.replace('../images/', '/images/');
  }
  if (node.type === 'heading' && Array.isArray(node.children)) {
    const i = node.children.findIndex(
      (c) => c.type === 'mdxTextExpression' && /^\/\*[\s\S]*\*\/$/.test(String(c.value).trim()),
    );
    if (i >= 0) {
      const id = String(node.children[i].value).trim().slice(2, -2).trim();
      node.data = node.data || {};
      node.data.hProperties = {...(node.data.hProperties || {}), id};
      node.children.splice(i, 1);
      const prev = node.children[i - 1];
      if (prev && prev.type === 'text') prev.value = prev.value.replace(/\s+$/, '');
    }
  }
  if (Array.isArray(node.children)) node.children.forEach(walk);
}
