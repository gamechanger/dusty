# Dusty Testing Specs
These specs are used to specify tests you can run in apps and libs. These do not exist as distinct documents but as subfields of lib and app specs. They are found under the **test** key.

## Keys

### image and build
The image and build keys in test specs mirror the image and build keys in the [app-spec](./app-specs.md#build).

### services
```
services:
  - testMongo
  - testRedis
```
The services key represents a list of services that the app or lib being tested depends on. These services will be spun up and daisy chained together over the Docker network bridge.  This is done using Docker Compose's **net** key.

### once
```
once:
  - pip install -r test_requirements.txt
```
The once key is a list of commands to be run when you are creating the testing base image.  In order to speed up the process of running tests, the first time tests are run, Dusty will create a testing base image based off of the image or build key and the once commands. This image is then used to run the actual tests.  This allows the heavy install commands to only happen the very first time tests are run. From there forward, tests should run very fast. <br />

### suites
```
suites:
  - name: frontend
    command:
      - ./manage.py test frontend
    description: test of gcweb through django
```
The suites key provides a list of tests that can be run for the app or lib.
**name** defines what you need to call to run the test.  If the testing spec is in an app named app1, you would be able to call the following:
* `dusty test app1 frontend`

Arguments can be passed to the tests in much the same way as the app's script key.

### compose
The compose key mirrors exactly the compose key in the [app-spec](./app-specs.md)
