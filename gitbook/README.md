---
description: The library for web and native user interfaces
layout:
  width: wide
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: true
  outline:
    visible: false
  pagination:
    visible: true
---

# React

<div align="center"><figure><img src="assets/react-logo.svg" alt="React logo" width="160"><figcaption></figcaption></figure></div>

<p align="center"><a href="learn/index.md" class="button primary">Learn React</a> <a href="reference/react/index.md" class="button secondary">API Reference</a></p>

***

## Create user interfaces from components

{% columns %}
{% column width="50%" %}
React lets you build user interfaces out of individual pieces called components. Create your own React components like `Thumbnail`, `LikeButton`, and `Video`. Then combine them into entire screens, pages, and apps.

Whether you work on your own or with thousands of other developers, using React feels the same. It is designed to let you seamlessly combine components written by independent people, teams, and organizations.

{% endcolumn %}

{% column %}
```jsx
function Video({ video }) {
  return (
    <div>
      <Thumbnail video={video} />
      <a href={video.url}>
        <h3>{video.title}</h3>
        <p>{video.description}</p>
      </a>
      <LikeButton video={video} />
    </div>
  );
}
```
{% endcolumn %}
{% endcolumns %}

***

## Write components with code and markup

{% columns %}
{% column width="50%" %}
React components are JavaScript functions. Want to show some content conditionally? Use an `if` statement. Displaying a list? Try array `map()`. Learning React is learning programming.

This markup syntax is called JSX. It is a JavaScript syntax extension popularized by React. Putting JSX markup close to related rendering logic makes React components easy to create, maintain, and delete.

{% endcolumn %}

{% column %}
```jsx
function VideoList({ videos, emptyHeading }) {
  const count = videos.length;
  let heading = emptyHeading;
  if (count > 0) {
    const noun = count > 1 ? 'Videos' : 'Video';
    heading = count + ' ' + noun;
  }
  return (
    <section>
      <h2>{heading}</h2>
      {videos.map(video =>
        <Video key={video.id} video={video} />
      )}
    </section>
  );
}
```
{% endcolumn %}
{% endcolumns %}

***

## Add interactivity wherever you need it

{% columns %}
{% column width="50%" %}
React components receive data and return what should appear on the screen. You can pass them new data in response to an interaction, like when the user types into an input. React will then update the screen to match the new data.

You don’t have to build your whole page in React. Add React to your existing HTML page, and render interactive React components anywhere on it.

<a href="learn/add-react-to-an-existing-project.md" class="button secondary">Add React to your page</a>

{% endcolumn %}

{% column %}
```jsx
import { useState } from 'react';

function SearchableVideoList({ videos }) {
  const [searchText, setSearchText] = useState('');
  const foundVideos = filterVideos(videos, searchText);
  return (
    <>
      <SearchInput
        value={searchText}
        onChange={newText => setSearchText(newText)} />
      <VideoList
        videos={foundVideos}
        emptyHeading={`No matches for “${searchText}”`} />
    </>
  );
}
```
{% endcolumn %}
{% endcolumns %}

***

## Go full-stack with a framework

{% columns %}
{% column width="50%" %}
React is a library. It lets you put components together, but it doesn’t prescribe how to do routing and data fetching. To build an entire app with React, we recommend a full-stack React framework like [Next.js](https://nextjs.org) or [React Router](https://reactrouter.com).

React is also an architecture. Frameworks that implement it let you fetch data in asynchronous components that run on the server or even during the build. Read data from a file or a database, and pass it down to your interactive components.

<a href="learn/creating-a-react-app.md" class="button secondary">Get started with a framework</a>

{% endcolumn %}

{% column %}
```jsx
import { db } from './database.js';
import { Suspense } from 'react';

async function ConferencePage({ slug }) {
  const conf = await db.Confs.find({ slug });
  return (
    <ConferenceLayout conf={conf}>
      <Suspense fallback={<TalksLoading />}>
        <Talks confId={conf.id} />
      </Suspense>
    </ConferenceLayout>
  );
}

async function Talks({ confId }) {
  const talks = await db.Talks.findAll({ confId });
  const videos = talks.map(talk => talk.video);
  return <SearchableVideoList videos={videos} />;
}
```
{% endcolumn %}
{% endcolumns %}

***

## Use the best from every platform

People love web and native apps for different reasons. React lets you build both web apps and native apps using the same skills. It leans upon each platform’s unique strengths to let your interfaces feel just right on every platform.

{% columns %}
{% column %}
### Stay true to the web

People expect web app pages to load fast. On the server, React lets you start streaming HTML while you’re still fetching data, progressively filling in the remaining content before any JavaScript code loads. On the client, React can use standard web APIs to keep your UI responsive even in the middle of rendering.
{% endcolumn %}

{% column %}
### Go truly native

People expect native apps to look and feel like their platform. [React Native](https://reactnative.dev) and [Expo](https://github.com/expo/expo) let you build apps in React for Android, iOS, and more. They look and feel native because their UIs _are_ truly native. It’s not a web view—your React components render real Android and iOS views provided by the platform.
{% endcolumn %}
{% endcolumns %}

With React, you can be a web _and_ a native developer. Your team can ship to many platforms without sacrificing the user experience. Your organization can bridge the platform silos, and form teams that own entire features end-to-end.

<a href="https://reactnative.dev/" class="button secondary">Build for native platforms</a>

***

## Upgrade when the future is ready

React approaches changes with care. Every React commit is tested on business-critical surfaces with over a billion users. Over 100,000 React components at Meta help validate every migration strategy.

The React team is always researching how to improve React. Some research takes years to pay off. React has a high bar for taking a research idea into production. Only proven approaches become a part of React.

#### Latest React news

<table data-view="cards">
  <thead>
    <tr><th></th><th></th><th data-hidden data-card-target data-type="content-ref"></th></tr>
  </thead>
  <tbody>
    <tr><td><strong>React 19.3</strong></td><td>September 9, 2026</td><td><a href="blog/2026/09/09/react-19-3.md">blog/2026/09/09/react-19-3.md</a></td></tr>
    <tr><td><strong>The React Foundation: A New Home for React Hosted by the Linux Foundation</strong></td><td>February 24, 2026</td><td><a href="blog/2026/02/24/the-react-foundation.md">blog/2026/02/24/the-react-foundation.md</a></td></tr>
    <tr><td><strong>Additional Vulnerabilities in RSC</strong></td><td>December 11, 2025</td><td><a href="blog/2025/12/11/denial-of-service-and-source-code-exposure-in-react-server-components.md">blog/2025/12/11/denial-of-service-and-source-code-exposure-in-react-server-components.md</a></td></tr>
    <tr><td><strong>Vulnerability in React Server Components</strong></td><td>December 3, 2025</td><td><a href="blog/2025/12/03/critical-security-vulnerability-in-react-server-components.md">blog/2025/12/03/critical-security-vulnerability-in-react-server-components.md</a></td></tr>
  </tbody>
</table>

<a href="blog/index.md" class="button secondary">Read more React news</a>

***

## Join a community of millions

You’re not alone. Two million developers from all over the world visit the React docs every month. React is something that people and teams can agree on.

<table data-view="cards">
  <thead>
    <tr><th></th><th data-hidden data-card-cover data-type="files"></th></tr>
  </thead>
  <tbody>
    <tr><td>People singing karaoke at React Conf</td><td><a href="images/home/community/react_conf_fun.webp">react_conf_fun.webp</a></td></tr>
    <tr><td>Sunil Pai speaking at React India</td><td><a href="images/home/community/react_india_sunil.webp">react_india_sunil.webp</a></td></tr>
    <tr><td>A hallway conversation between two people at React Conf</td><td><a href="images/home/community/react_conf_hallway.webp">react_conf_hallway.webp</a></td></tr>
    <tr><td>A hallway conversation at React India</td><td><a href="images/home/community/react_india_hallway.webp">react_india_hallway.webp</a></td></tr>
    <tr><td>Elizabet Oliveira speaking at React Conf</td><td><a href="images/home/community/react_conf_elizabet.webp">react_conf_elizabet.webp</a></td></tr>
    <tr><td>People taking a group selfie at React India</td><td><a href="images/home/community/react_india_selfie.webp">react_india_selfie.webp</a></td></tr>
    <tr><td>Nat Alison speaking at React Conf</td><td><a href="images/home/community/react_conf_nat.webp">react_conf_nat.webp</a></td></tr>
    <tr><td>Organizers greeting attendees at React India</td><td><a href="images/home/community/react_india_team.webp">react_india_team.webp</a></td></tr>
  </tbody>
</table>

This is why React is more than a library, an architecture, or even an ecosystem. React is a community. It’s a place where you can ask for help, find opportunities, and meet new friends. You will meet both developers and designers, beginners and experts, researchers and artists, teachers and students. Our backgrounds may be very different, but React lets us all create user interfaces together.

***

<h2 align="center">Welcome to the React community</h2>

<p align="center"><a href="learn/index.md" class="button primary">Get Started</a></p>
