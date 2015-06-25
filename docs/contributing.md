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

* Update the changelog
  * Add a date to the changelog for this version
  * Add a new version that has an `In progress` title rather than a date
  * Update the changelog to reflect your new changes with appropriate descriptions
    * NEW: This change is an addition to the existing code/functionality, and should include a description of what the addition does.
    * BREAKING: This update changes the existing promises of the dusty CLI API or specs API
    * FIXED: This is a patch for something broken in the current dusty version
    * other comments: anything that is not one of the above
  * Submit a pull request for your changelog updates and merge once accepted

* Cut a new version of Dusty
  * Run the `DustyRelease` Jenkins job with your new version number supplied as a parameter

* Update README.md to reflect the new Dusty version
  * After the `DustyRelease` Jenkins job has successfully run, change the curl target specified in the readme to reference the newly minted version
  * Create a pull request for this change and merge once accepted

* Bump the version number dusty/constants.py to the *next* version assigned to the `VERSION` variable
