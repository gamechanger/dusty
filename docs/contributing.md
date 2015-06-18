# Contributing

## Asking for Help

Please run a `dusty dump`, save the results to a [gist](https://gist.github.com/),
and include a link to the gist in any bug reports.

## Running Tests

Unit tests are pretty simple:

```
$ nosetests tests/unit
```

Integration tests must be run on OS X and are a bit trickier. Be aware
that integration tests may alter or delete existing Dusty information
on your system, including but not limited to your config, Dusty-managed
repos, and boot2docker VM.

The recommended approach is to let the Jenkins server run these for you
when you submit a PR.

```
# Integration tests run against an actual Dusty daemon
$ sudo launchctl stop org.gamechanger.dusty
$ sudo dusty -d & # launch a daemon based on your checked out code
$ DUSTY_ALLOW_INTEGRATION_TESTS=yes nosetests tests/integration
```

## Building Docs

Docs are built with [MkDocs](http://www.mkdocs.org/). For development, you can
run the following in the root Dusty directory:
```
$ pip install mkdocs
$ mkdocs serve
```

## Release Checklist

Before a new release, please do the following:

* Add a date to the changelog for this version
* Run the `DustyRelease` Jenkins job with your new version number
* Bump the version number in dusty/constants.py to the *next* version
* Bump the version of the curl command on the Readme
