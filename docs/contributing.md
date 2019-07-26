# Contributing

## Asking for Help

Please run a `dusty dump`, save the results to a [gist](https://gist.github.com/),
and include a link to the gist in any bug reports.

## Running Locally

If dusty is already installed and its running as a system daemon,
that needs to be stopped first:

```
$ sudo launchctl unload /Library/LaunchDaemons/com.gamechanger.dusty.plist
```

You can verify dusty daemon is not running by checking `ps`:

```
$ ps aux | grep dusty | grep -v grep | wc -l
```

Now you can install dusty as a Python package:

```
$ git clone git@github.com:gamechanger/dusty.git
$ cd dusty
$ virtualenv --python=$(which python2.7) venv
$ source venv/bin/activate
$ python -m pip install -e .
```

Since it is installed as a source distribution `dusty` should resolve to within virtualenv:

```
$ which dusty
$ dusty -v
```

Alternatively dusty can be invoked as Python module:

```
$ python -m dusty.cli -v
```

To use dusty daemon needs to be running which can be started with:

```
$ python -m dusty.cli -d
```

Note that it will run as a foreground process which is useful to monitor daemon log output.

## Running Tests

Install test deps:

```
$ pip install -r requirements-dev.txt
```

Unit tests are pretty simple:

```
$ nosetests tests/unit
```

Integration tests are also provided which test against an actual running
Dusty daemon. A script is provided to help run these inside the `tests`
folder.

**WARNING**: Integration tests may alter or delete existing Dusty
information on your system, including but not limited to your config,
Dusty-managed repos, active containers, and Docker VM.

```
$ ./tests/run_integration_tests.sh # run all tests
$ ./tests/run_integration_tests.sh cli/bundles_test.py # run specific modules inside tests/integration
```

## Building Docs

Docs are built with [MkDocs](http://www.mkdocs.org/). For development, you can
run the following in the root Dusty directory:
```
$ pip install mkdocs
$ mkdocs serve
```

## Maintaining the Changelog

User-facing changes should be documented in the Changelog as they are merged. Changes are segmented
into one of three types:

* **Breaking**: Changes to the existing Dusty CLI, specs, or runtime environment which are not backwards-compatible
* **New**: A new user-facing feature, or something that enables a workflow that wasn't possible before.
* **Misc**: Anything else! Typically bug fixes or notable changes to implementation details.

## Release Checklist

* Update the changelog
    * Add a date to the changelog for this version
    * Add a new version with `(In Progress)` after it

* Update [Installation](installation.md) to point to the binary for your new version

* Cut a new release by running the `DustyRelease` Jenkins job with your new version number

* Bump the version number in `dusty/constants.py` to the new, in-progress version

* Go update the release on GitHub to include the new version's notes from the changelog

* Follow [Homebrew's instructions](https://github.com/caskroom/homebrew-cask/blob/master/CONTRIBUTING.md#updating-a-cask) to update our cask
