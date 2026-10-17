---
title: "Built-in React APIs"
---

<Intro>

In addition to [Hooks](hooks.md) and [Components](components.md), the `react` package exports a few other APIs that are useful for defining components. This page lists all the remaining modern React APIs.

</Intro>

---

* [`createContext`](createContext.md) lets you define and provide context to the child components. Used with [`useContext`.](useContext.md)
* [`lazy`](lazy.md) lets you defer loading a component's code until it's rendered for the first time.
* [`memo`](memo.md) lets your component skip re-renders with same props. Used with [`useMemo`](useMemo.md) and [`useCallback`.](useCallback.md)
* [`startTransition`](startTransition.md) lets you mark a state update as non-urgent. Similar to [`useTransition`.](useTransition.md)
* [`addTransitionType`](addTransitionType.md) lets you specify the cause of a Transition. Used with [`startTransition`](startTransition.md) and [`<ViewTransition>`.](ViewTransition.md)
* [`act`](act.md) lets you wrap renders and interactions in tests to ensure updates have processed before making assertions.
* [`cache`](cache.md) lets you cache the result of a data fetch or computation.
* [`cacheSignal`](cacheSignal.md) lets you know when the `cache()` lifetime is over.
* [`captureOwnerStack`](captureOwnerStack.md) reads the current Owner Stack in development and returns it as a string if available.

---

## Resource APIs

*Resources* can be accessed by a component without having them as part of their state. For example, a component can read a message from a Promise or read styling information from a context.

You can pass these types of resources to [`use`](use.md):

* A [Promise](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise) to read its resolved value.
* A [context](../../learn/passing-data-deeply-with-context.md) to read its value.
* The value returned by [`browser`](../react-dom/browser.md) to mark a component as browser-only during server rendering.

```js
function MessageComponent({ messagePromise }) {
  const message = use(messagePromise);
  const theme = use(ThemeContext);
  use(browser());
  // ...
}
```
