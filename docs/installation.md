# Installing Dusty

## Requirements
You must have the following installed in order to run Dusty:

 * [nginx](http://wiki.nginx.org/Main)
 * [Virtualbox](https://www.virtualbox.org/wiki/VirtualBox)
 * [boot2docker](http://boot2docker.io/)
 * [Docker Compose](https://docs.docker.com/compose/)

Not all versions of these programs will work with Dusty.  Dusty
will warn you if you have a version installed that may be too old.
We recommend brew-installing the latest versions of each of these
programs:

## WARNING
The most recent version of VirtualBox, [VirtualBox 5.0](https://www.virtualbox.org/wiki/Changelog), is [not compatible](https://github.com/gamechanger/dusty/issues/383) with the current version of boot2docker.
Please install <strong>VirtualBox 4.X</strong> in order to run Dusty.

```
brew update
which nginx || brew install nginx
which boot2docker || brew install boot2docker
which docker-compose || brew install docker-compose
```

## Installation

To download and install Dusty, run:
```
bash -c "`curl -L https://github.com/gamechanger/dusty/releases/download/0.2.1/install.sh`"
```

This script will install Dusty as a service and run the preflight check to ensure that all
dependencies are installed. If the script throws an error, make sure to resolve that before
continuing.

If that worked, [continue to Setup.](setup.md)
