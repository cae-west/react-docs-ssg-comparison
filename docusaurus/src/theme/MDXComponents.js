// Stand-ins for React's custom MDX components, registered through Docusaurus's
// theme layer. The content files are NOT modified; this file only tells
// Docusaurus how to render tags that react.dev defines in its own site code.
import React from 'react';
import MDXComponents from '@theme-original/MDXComponents';
import Admonition from '@theme/Admonition';
import Details from '@theme/Details';
import useBaseUrl from '@docusaurus/useBaseUrl';

const callout = (type, title) => ({children}) => (
  <Admonition type={type} title={title}>{children}</Admonition>
);
const collapsible = (summary) => ({children}) => (
  <Details summary={summary}>{children}</Details>
);
const Passthrough = ({children}) => <>{children}</>;
const Hidden = () => null;
const Block = ({children}) => <div>{children}</div>;
const Inline = ({children}) => <span>{children}</span>;

function Figure({src, alt = '', caption, name, children}) {
  const url = useBaseUrl(src || `/images/docs/diagrams/${name}.png`);
  return (
    <figure style={{textAlign: 'center'}}>
      <img src={url} alt={alt} style={{maxWidth: '100%'}} />
      {caption && <figcaption>{caption}</figcaption>}
      {children}
    </figure>
  );
}

const Terminal = ({children}) => <pre><code>{children}</code></pre>;

export default {
  ...MDXComponents,
  // Callouts
  Intro: ({children}) => <div className="react-intro" style={{fontSize: '1.15rem', marginBottom: '1.5rem'}}>{children}</div>,
  Note: callout('note', 'Note'),
  Pitfall: callout('warning', 'Pitfall'),
  DeepDive: callout('info', 'Deep Dive'),
  YouWillLearn: callout('info', 'You will learn'),
  Recap: callout('tip', 'Recap'),
  LearnMore: callout('info', 'Learn more'),
  Deprecated: callout('danger', 'Deprecated'),
  Experimental: callout('caution', 'Experimental'),
  // Collapsibles
  Hint: collapsible('Hint'),
  Solution: collapsible('Solution'),
  // Interactive sandboxes: no live editor in Docusaurus, so only the code blocks inside show
  Sandpack: Block, SandpackRSC: Block, SandpackWithHTMLOutput: Block,
  Challenges: Block, Recipes: Block, RSC: Block,
  // Images
  Illustration: Figure, IllustrationBlock: Block, Diagram: Figure, DiagramGroup: Block, CodeDiagram: Block,
  // Console / terminal
  TerminalBlock: Terminal, ConsoleBlock: Terminal, ConsoleBlockMulti: Terminal, ConsoleLogLine: Block,
  // Inline
  CodeStep: ({children}) => <mark>{children}</mark>,
  MathI: Inline, Math: Block,
  ExperimentalBadge: Inline, CanaryBadge: Inline, Wip: Block,
  // Table of contents: Docusaurus already renders one on the right
  InlineToc: Hidden,
  // Not available without react.dev's site code
  YouTubeIframe: Hidden, TeamMember: Block, BlogCard: Block, ErrorDecoder: Hidden,
  // Plain JSX names that appear in prose
  LanguageList: Passthrough, App: Passthrough, StrictMode: Passthrough, Fragment: Passthrough,
  LazyProductDetailPage: Passthrough, FeaturedProducts: Passthrough, Suspense: Passthrough,
  ViewTransition: Passthrough, Profiler: Passthrough, Activity: Passthrough, FullWidth: Passthrough,
};
