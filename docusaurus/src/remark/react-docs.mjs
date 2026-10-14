// Docusaurus-side adapter for react.dev conventions. Runs while the pages are
// compiled, so the content files themselves are never changed.
//  1. Images written as ../images/x.png work on react.dev (the browser resolves
//     them from the page URL) but Docusaurus resolves them from the file's folder.
//     Point them at /images/x.png, where the copied images are served.
//  2. react.dev headings carry explicit anchor ids as  ## Usage {/*usage*/}.
//     Docusaurus doesn't read that syntax, so apply the id to the heading.
export default function reactDocsRemark() {
  return (tree) => walk(tree);
}

function walk(node) {
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
