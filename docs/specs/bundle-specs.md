# Bundle Specs

Bundles are logical groups of applications that are toggleable by users at
runtime. Bundles are primarily used to hide the implementation details of
a particular service from endusers. Instead of having to activate the five
applications which compose a logical service, the user instead simply activates
the bundle for the logical service and lets Dusty do the rest.

Bundle specs must be placed in the `bundles` subfolder of your specs repo.

## description

```
description: The user authentication service
```

A short text description of the logical service defined by the bundle.
This is exposed to the user by `dusty bundles list`.

## apps

```
apps:
  - servicerouter
  - userauth
```

The list of apps to be run by `dusty up` if this bundle is activated.
These apps are used as entrypoints into the dependency graph defined by
your app and service specs.
