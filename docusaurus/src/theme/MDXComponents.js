// Stand-ins for React's custom MDX components, styled after the originals in
// react.dev/src/components/MDX. Registered through Docusaurus's theme layer;
// the content files are NOT modified.
import React from 'react';
import MDXComponents from '@theme-original/MDXComponents';
import useBaseUrl from '@docusaurus/useBaseUrl';

const Passthrough = ({children}) => <>{children}</>;
const Hidden = () => null;
const Block = ({children}) => <div>{children}</div>;
const Inline = ({children}) => <span>{children}</span>;

// Colored callouts (Note, Pitfall, ...) as in ExpandableCallout.tsx
const callout = (variant, title) => ({children}) => (
  <div className={`rd-callout rd-${variant}`}>
    <h3 className="rd-callout-title">{title}</h3>
    <div>{children}</div>
  </div>
);
// Gray cards (Recap, You will learn, ...) as in SimpleCallout.tsx
const card = (title) => ({children}) => (
  <div className="rd-card">
    <h3 className="rd-card-title">{title}</h3>
    <div>{children}</div>
  </div>
);
const hint = (label) => ({children}) => (
  <details className="rd-hint"><summary>{label}</summary>{children}</details>
);

function Figure({src, alt = '', caption, name, children}) {
  const url = useBaseUrl(src || `/images/docs/diagrams/${name}.png`);
  return (
    <figure className="rd-figure">
      <img src={url} alt={alt} />
      {caption && <figcaption>{caption}</figcaption>}
      {children}
    </figure>
  );
}

// Static stand-in for the live Sandpack editor: shows each file's code,
// labelled with its file name when Docusaurus exposes the code-fence meta.
function Sandpack({children}) {
  const items = React.Children.toArray(children).map((child, i) => {
    let label = null;
    try {
      const code = child && child.props && child.props.children;
      const meta = (code && code.props && (code.props.metastring || code.props.meta)) || '';
      label = String(meta).split(/\s+/).find((t) => /\.\w+$/.test(t)) || null;
    } catch (e) { /* keep unlabeled */ }
    return (
      <React.Fragment key={i}>
        {label && <div className="rd-sandpack-file">{label}</div>}
        {child}
      </React.Fragment>
    );
  });
  return <div className="rd-sandpack">{items}</div>;
}

const Terminal = ({children}) => <div className="rd-terminal"><pre style={{margin: 0, background: 'transparent', color: 'inherit'}}>{children}</pre></div>;

export default {
  ...MDXComponents,
  Intro: ({children}) => <div className="react-intro">{children}</div>,
  Note: callout('note', 'Note'),
  Pitfall: callout('pitfall', 'Pitfall'),
  Deprecated: callout('deprecated', 'Deprecated'),
  Experimental: callout('experimental', 'Experimental Feature'),
  Wip: callout('wip', 'Under Construction'),
  RSC: callout('blue', 'React Server Components'),
  YouWillLearn: card('You will learn'),
  Recap: card('Recap'),
  LearnMore: card('Learn more'),
  DeepDive: ({children}) => (
    <details className="rd-deepdive"><summary>Deep Dive</summary>{children}</details>
  ),
  Hint: hint('Show hint'),
  Solution: hint('Show solution'),
  Challenges: ({children}) => <div className="rd-challenges">{children}</div>,
  Sandpack, SandpackRSC: Sandpack, SandpackWithHTMLOutput: Sandpack,
  Recipes: Block,
  Illustration: Figure, Diagram: Figure,
  IllustrationBlock: Block, DiagramGroup: Block, CodeDiagram: Block,
  TerminalBlock: Terminal, ConsoleBlock: Terminal, ConsoleBlockMulti: Terminal, ConsoleLogLine: Block,
  CodeStep: ({children}) => <mark>{children}</mark>,
  MathI: Inline, Math: Block,
  ExperimentalBadge: Inline, CanaryBadge: Inline,
  InlineToc: Hidden,
  YouTubeIframe: Hidden, TeamMember: Block, BlogCard: Block, ErrorDecoder: Hidden,
  LanguageList: Passthrough, App: Passthrough, StrictMode: Passthrough, Fragment: Passthrough,
  LazyProductDetailPage: Passthrough, FeaturedProducts: Passthrough, Suspense: Passthrough,
  ViewTransition: Passthrough, Profiler: Passthrough, Activity: Passthrough, FullWidth: Passthrough,
};
