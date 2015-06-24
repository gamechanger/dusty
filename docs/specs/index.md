# Dusty Specs Overview
There are 4 main types of objects in Dusty.<br/>
1. [Bundles](./bundle-specs.md) - highest level objects in Dusty.  They can be activated or deactivated.  Bundles are organized in logical groups, like the website or api. `dusty up` will run the set of activated bundles.<br/>
2. [Apps](./app-specs.md) - objects that should run in their own container and have code from the user.<br/>
3. [Services](./service-specs.md) - objects that should run in their own container but uses external code (mongo or redis instance).<br/>
4. [Libs](./lib-specs.md) - objects that have code from the user, but do not run in their own container. These will be included in app containers for app code to use.

There is a 5th subtype that is important enough to get its own spec page.<br/>
5. [Tests](./test-specs.md) - objects found on both the lib and apps objects. They define how to run tests on a user's app and lib code.

## Dusty Specs Repo
The dusty specs repo is organized as follows.
```
dusty-specs/
  apps/
  bundles/
  libs/
  services/
```

## Note About Commands
All commands specified in dusty, be they app's once and always, scripts, tests, ...etc are put in a shell file and run using sh.  This allows some more flexibility of what types of commands we allow, including running commands in the background (&).
