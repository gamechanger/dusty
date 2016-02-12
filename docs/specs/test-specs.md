# Test Specs

These specs are used to specify tests you can run in apps and libs. These do not exist as distinct documents but as subfields of lib and app specs. They are found under the **test** key.

## How Dusty Runs Tests

To facilitate quick turnaround times with testing, Dusty does the following to run tests:

1. Pull or create the image defined in `image` or `build`
2. Run the `once` script and commit the resulting image locally
3. Use the image from Step 2 as the starting point for all test suite runs

## image

```
image: ubuntu:15.04
```

`image` specifies a Docker image on which to base the container used to create the
intermediate testing image. If the image does not exist locally, Dusty will pull it.

If the `image` is hosted in a private registry which requires authentication,
you can add `image_requires_login: True` to force the user to authenticate
before Dusty attempts to pull down the image.

Either `build` or `image` must be supplied in the test spec. They cannot both be supplied.

## build

```
build: .
```

`build` specifies a directory containing a Dockerfile on the host OS which will be used
to build the intermediate testing image.

This path can be absolute or relative. If it is relative, it is relative to repo directory
on the host OS.

Either `build` or `image` must be supplied in the spec. They cannot both be supplied.

## once

```
once:
  - pip install -r test_requirements.txt
```

`once` specifies the commands used in Step 2 of test image creation to create a final
testing image. The resulting image is committed locally and used as the starting point
for test suite runs.

Expensive install steps should go in `once` so that Dusty can cache their results.

## suites

`suites` specifies a list of test suites available for this app or lib. Each suite provides
`name` and `description` keys which are shown when using the `dusty test` command.

Each suite may also contain the following keys:

### services

```
services:
  - testMongo
  - testRedis
```

`services` provides a list of Dusty services which will be linked to the test container for this
suite. Containers are spun up for each service and linked to the final test container. All containers
for a given test suite are also connected to the same network stack. This allows your testing
container to access ports exposed by any test services through its own `localhost`.

Unlike runtime container dependencies, each test suite gets its own copy of the service containers.
This provides service isolation across multiple apps and test suites.

### command

```
command:
  - nosetests
```

`command` defines the script to be run to perform the test for this suite.

Tests can accept arguments at runtime through the `dusty test` command.  Arguments are passed through
to the final command specified by the `command` list for the suite.

### default_args

```
default_args: tests/unit
```

`default_args` allows you to specify arguments which are passed to the final command in the
suite's `command` list if no arguments are given at runtime. If the user provides arguments to
the `dusty test` command, the `default_args` are ignored.

In this example, the following Dusty commands would cause the following commands to be run inside
the suite's container:

```
> dusty test my-app suiteName
=> nosetests tests/unit

> dusty test my-app suiteName tests/integration
=> nosetests tests/integration
```

### compose

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
