// Stand-in for next/link, so the original react.dev homepage code runs in Docusaurus.
import React from 'react';
import Link from '@docusaurus/Link';
export default function NextLink({href, children, legacyBehavior, passHref, prefetch, scroll, replace, shallow, locale, ...rest}) {
  const to = typeof href === 'string' ? href : (href && href.pathname) || '/';
  return <Link to={to} {...rest}>{children}</Link>;
}
