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
$ sudo launchctl stop com.gamechanger.dusty
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

## Maintaining the Changelog

User-facing changes should be documented in the Changelog as they are merged. The following
types of changes should be prefixed with the appropriate change type:

* BREAKING CHANGE: Changes to the existing Dusty CLI, specs, or runtime environment which are not backwards-compatible
* NEW: A new user-facing feature, or something that enables a workflow that wasn't possible before.
* FIXED: Noteworthy, user-facing bug fixes.

Any changes which do not meet any of these definitions but do affect the user experience
may be listed without a prefix.

## Release Checklist

* Update the changelog
    * Add a date to the changelog for this version
    * Add a new version with `(In Progress)` after it

* Update [Installation](installation.md) to point to the binary for your new version

* Cut a new release by running the `DustyRelease` Jenkins job with your new version number

* Bump the version number in `dusty/constants.py` to the new, in-progress version
