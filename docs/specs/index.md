# Dusty Specs Overview
There are 4 main types of objects in Dusty.
1. [Bundles](.bundle-specs) - highest level objects in Dusty.  They can be activated or deactivated.  Bundles are organized in logical groups, like the website or api. `dusty up` will run the set of activated bundles.
2. [Apps](./app-specs) - objects that should run in their own container and have code from the user.
3. [Services](./service-specs) - objects that should run in their own container but uses external code (mongo or redis instance).
4. [Libs](./lib-specs) - objects that have code from the user, but do not run in their own container. These will be included in app containers for app code to use.

There is a 5th subtype that is important enough to get its own spec page.
5. [Tests](./testing-specs) - objects found on both the lib and apps objects. They define how to run tests on a users app and lib code.

## Dusty Specs Repo
The dusty specs repo is organized as follows.
```
dusty-specs/
  apps/
  bundles/
  libs/
  services/
```
