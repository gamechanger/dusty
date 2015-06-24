# Dusty Bundle Specs
These specs are used to specify bundles for you local environment. They should go in the bundles folder in your specs repo.

## Keys

### description
```
description: The website! Does not include the iOS app API.
```
The description key tells what this bundle is for.  It is exposed to the user when they type `dusty bundles list`.

### apps
```
apps:
  - app1
  - app2
```
The apps key specifies a list of apps to launch for this bundle. Dusty will launch these apps when `dusty up` is called.
