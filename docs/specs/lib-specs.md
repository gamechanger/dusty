# Dusty Lib Specs
These specs are used to specify libs in your local environment. They should go in the libs folder in your specs repo.

## Keys

### repo and mount
The **repo** and **mount** keys are almost identical to those found in the [app specs](./app-specs.md). The only difference is that both repo and mount are required in the lib spec.

### install
```
install:
  - python setup.py install --force
```
The install key is used to specify a list of commands that should be run to prepare the library to be used. This command is run in the app's container, prior to the apps once and always commands being run.

### depends
```
depends:
  libs:
    - lib2
    - lib3
```
The depends key allows a lib to specify other libs that it depends on. A lib can only depend other libs.

### test
```
test:
    ...
```
Libs contain the test key.  To find out more about the sub test spec, visit the [testing spec page](./testing-specs.md).
