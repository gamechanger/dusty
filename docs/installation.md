# Installing Dusty

## Requirements
You must have the following installed in order to run Dusty:

 * nginx
 * Virtualbox
 * boot2docker
 * Docker Compose

Not all versions of these programs will work with Dusty.  Dusty
will warn you if you have a version installed that may be too old.
We recommend brew-installing the latest versions of each of these
programs:
```
brew install nginx
brew install boot2docker
brew install docker-compose
```

## Installation

We provide a install script with each release. The install script should work
to install Dusty from scratch, as well as to update Dusty to a new version.

This install script takes the following actions:

* Downloads the Dusty binary, and places it at `/usr/local/bin/dusty`
* Unloads any existing Dusty Daemon plist from `/System/Library/LaunchDaemons/org.gamechanger.dusty.plist`
* Downloads our plist file to the same location
* Runs Dusty with `--preflight-only`, which will check some components of your system setup
* Loads the plist that was downloaded, if the previous step was successful

To download and run this install script:
```
bash -c "`curl -L https://github.com/gamechanger/dusty/releases/download/0.1.1/install.sh`"
```

