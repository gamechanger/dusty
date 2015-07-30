# Lib Specs

Libs define additional repos which are maintained by Dusty and mounted into running
app containers which depend on them. Dusty can keep your libs' repos up to date and
ensure their install commands are run when necessary inside app containers to keep
the container's state clean.

## repo

```
repo: github.com/my-org/my-app
  -or-
repo: http://github.com/my-org/my-app.git
  -or-
repo: /Users/myuser/my-app
```

`repo` specifies the repo containing the source for a lib. By default, Dusty manages this
repo for you and will keep its local copy up to date. Once a repo is defined in an active spec,
it can be controlled using the `dusty repos` command.

Repos can be specified using either a URL or an absolute path to a Git repo on your local filesystem.
If a repo URL starts with http, http will be used to clone the repo.  Note that this will only work
with public repositories.  By default, ssh is used to clone repos.

`repo` is required in lib specs.

## mount

```
mount: /my-app
```

`mount` tells Dusty where to mount the contents of the lib's repo inside any app containers
which depend on it.

`mount` is required in lib specs.

## install

```
install:
  - python setup.py install
```

`install` specifies a list of commands that should be run to prepare the library to be used.
This command is run in the container of an app which depends on the lib.

Lib install commands are executed prior to the app's `once` and `always` commands during
container startup.

## depends

```
depends:
  libs:
    - lib2
    - lib3
```

`depends` is used to specify other libs which should be installed inside any app container
which depends on this lib. Only `libs` may be specified inside a lib's `depends` key.

## test

```
test:
  ...
```

The `test` key contains information on how to run tests for a lib. Once specified,
tests may be run with the `dusty test` command. To find out more about the testing spec,
see the [testing spec page](./test-specs.md).
