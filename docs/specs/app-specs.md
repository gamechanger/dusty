# App Specs

Apps define running containers based on source code under your control. App specs tell
Dusty how to run this container, including any dependencies the app may have on other
apps, services, or libs. You can also specify common scripts and testing commands for
an app in its spec.

By default, Dusty manages the source for an app for you and keeps it up to date automatically.
You can tell Dusty to use your own locally checked out copy of the source using `dusty repos`.

## repo

```
repo: github.com/my-org/my-app
  -or-
repo: /Users/myuser/my-app
```

`repo` specifies the repo containing the source for an app. By default, Dusty manages this
repo for you and will keep its local copy up to date. Once a repo is defined in an active spec,
it can be controlled using the `dusty repos` command.

Repos can be specified using either a URL or an absolute path to a Git repo on your local filesystem.

## mount

```
mount: /my-app
```

`mount` tells Dusty where to mount the contents of the repo inside the running container.

`mount` must be provided if `repo` is provided.

All Dusty commands (once and always) are started in the `mount` directory.  You might need to change to or copy from another directory.

## depends

```
depends:
  services:
    - myService1
    - myService2
  apps:
    - myOtherApp
  libs:
    - myLib
```

`depends` is used to specify what libs, apps and services this app depends on.

Containers for apps and services specified in the `depends` dict are created before the container
for the referencing app. The referencing app is then linked (using [Docker links](https://docs.docker.com/userguide/dockerlinks/))
to the dependent apps and services. Once containers are linked, they may reference each other through
the environment variables or `/etc/hosts` overrides provided by Docker links.

**N.B.:** All container links, including those from both `depends` and `conditional_links`, must be acyclical.

Dependent libs (and their lib dependencies) will be mounted into the running app container and
installed according to their specs.

## conditional_links

```
conditional_links:
  apps:
    - myConditionalApp
```

`conditional_links` specifies downstream apps which are not required by the referencing app but
should be linked if they are running as the result of a different bundle or dependency. This lets
you layer optional containers onto a stack without forcing them all to be run whenever the main
container is run.

Unlike `depends`, `conditional_links` do not support links to libs.

**N.B.:** All container links, including those from both `depends` and `conditional_links`, must be acyclical.

## host_forwarding

```
host_forwarding:
  - host_name: local.website.com
    host_port: 80
    container_port: 80
```

`host_forwarding` allows you to specify multiple routes which should be linked between your host OS
and the application running inside this app's container.

**host_name**: local hostname exposed on your host OS.
**host_port**: local port which routes through to the container port.
**container_port**: remote port the app is running on in the Docker container.

In this example, we would be able to go to `local.website.com:80` on our host OS and talk to
the process inside this app's container on port 80.

## image

```
image: ubuntu:15.04
```

`image` specifies a Docker image on which to base the container which will run this
app. If the image does not exist locally, Dusty will pull it.

Either `build` or `image` must be supplied in the spec. They cannot both be supplied.

## build

```
build: .
```

`build` specifies a directory containing a Dockerfile on the host OS which will be used
to build a new image to serve as the base image for this app's container.

This path can be absolute or relative. If it is relative, it is relative to repo directory
on the host OS.

Either `build` or `image` must be supplied in the spec. They cannot both be supplied.

## commands

```
commands:
  once:
    - apt-get update
    - apt-get install -qy python
  always:
    - python manage.py runserver --noreload
```

`commands` define scripts that are run at various points in a container's lifecycle. Two sub-commands are
supported: `once` and `always`.

`once`: Runs only the first time a container is started. Generally, this is run during a `dusty up`.
`always`: Runs every time the container is started, *after* the `once` script has run if it is the first time.
The `always` script must run the application's main process.

Generally, you will want to do expensive setup operations like installs inside `once`, then start your
application inside of `always`.

The output of the once command is logged inside the app's container at `/var/log/dusty_once_fn.log`.

## scripts

```
scripts:
  - name: grunt
    description: Build assets compiled by Grunt (CSS, JS, that sort of thing)
    command:
      - grunt build
```

`scripts` allows you to specify scripts that can be run inside the app's container. This is useful
for sharing common functionality across all users of the specs.

The `dusty scripts` command is used for introspection and execution of available scripts.

Scripts can accept arguments at runtime through the `dusty scripts` command.  Arguments are passed through
to the final command specified by the `command` list.

## compose

```
compose:
  environment:
    APP_ENVIRONMENT: local
    MONGO_HOST: persistentMongo
```

Dusty uses Docker Compose to create and manage containers. The `compose` key allows you to
override any of the values passed through to Docker Compose at runtime.

For more information on what you can override through this key, please see
the [Docker Compose specification](https://docs.docker.com/compose/yml/).

## test

```
test:
  ...
```

The `test` key contains information on how to run tests for an application. Once specified,
tests may be run with the `dusty test` command. To find out more about the testing spec,
see the [testing spec page](./test-specs.md).
