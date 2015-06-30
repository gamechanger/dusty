# Specs Overview

Dusty uses YAML specifications for configuration of the applications, services, and
libraries used to create your stack.

An additional entrypoint layer, called a Bundle, is used to provide toggleable entrypoints
into your stack's dependency graph. Users can decide which Bundles they want to run,
and Dusty runs the applications, services, and libraries defined by those Bundles.

1. [Bundles](./bundle-specs.md) -  Logical groups of applications. These can be
toggled by users at runtime to mix and match parts of the stack.
1. [Apps](./app-specs.md) -  Applications which you actively develop. These may link
to a source repo and install Libs. May include test specifications.
1. [Services](./service-specs.md) -  Applications which you do not develop. Services are
often used to run database containers off of a public Docker image.
1. [Libs](./lib-specs.md) -  Libraries which you actively develop. These may be depended on
by Apps, which will then install them automatically. May include test specifications.

Additionally, apps and libs share the following common sub-schemata -

* [Tests](./test-specs.md) -  Specifications of test images and suites. Libs and Apps with
test specs can be tested using `dusty test`.

## Dusty Specs Repo

Dusty assumes that your specs are defined in a Git repo with the following format -

```
/
  apps/
  bundles/
  libs/
  services/
```

Each folder must contain YAML files with specs which match the schema for that type. The
[example specs repo](https://github.com/gamechanger/dusty-example-specs) has valid
examples for each of these.
