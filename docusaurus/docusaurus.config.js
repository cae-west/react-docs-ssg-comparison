// @ts-check
import {themes as prismThemes} from 'prism-react-renderer';
import reactDocsRemark from './src/remark/react-docs.mjs';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'React Docs (Docusaurus)',
  tagline: 'The React documentation, rendered by Docusaurus',
  url: 'https://cae-west.github.io',
  baseUrl: process.env.DOCS_BASE_URL || '/',
  organizationName: 'cae-west',
  projectName: 'react-docs-ssg-comparison',

  future: {v4: true},

  // Content is unmodified React docs, so tolerate what the content assumes about react.dev.
  onBrokenLinks: 'warn',
  onBrokenAnchors: 'warn',
  markdown: {hooks: {onBrokenMarkdownLinks: 'warn', onBrokenMarkdownImages: 'warn'}},

  // Serve the copied images (public/images/...) from the site root, as react.dev does.
  staticDirectories: ['static', '../public'],

  i18n: {defaultLocale: 'en', locales: ['en']},

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          path: '../content',      // read the unmodified content in place
          routeBasePath: '/',      // docs at the site root, like react.dev
          sidebarPath: './sidebars.js',
          beforeDefaultRemarkPlugins: [reactDocsRemark],
        },
        blog: false,
        theme: {customCss: './src/css/custom.css'},
      }),
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'React',
      logo: {alt: 'React', src: 'img/logo.svg'},
      items: [
        {type: 'docSidebar', sidebarId: 'learn', position: 'left', label: 'Learn'},
        {type: 'docSidebar', sidebarId: 'reference', position: 'left', label: 'Reference'},
        {type: 'docSidebar', sidebarId: 'community', position: 'left', label: 'Community'},
        {type: 'docSidebar', sidebarId: 'blog', position: 'left', label: 'Blog'},
      ],
    },
    prism: {theme: prismThemes.github, darkTheme: prismThemes.dracula},
  },
};

export default config;
