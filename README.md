# dusty
Docker-based development environment manager



# Installation
Currently the recommended way to install dusty is to use our installation script, which will install the latest
version of dusty's binaries, and set up a dustyd daemon plist:
```
bash -c "`curl -L https://raw.githubusercontent.com/gamechanger/dusty/master/setup/install.sh`"
```

This will:
 * Add `dusty` and `dustyd` binaries inside /usr/local/bin
 * Put an `org.gamechanger.dustyd.plist` file in `/System/Library/LaunchDaemons`
 * Load the plist file (after unloading it, in case you're updating dusty)

The daemon will throw errors if any of its required programs aren't already installed:
 * VBoxManage
 * boot2docker
 * docker-compose
 * nginx

# Basics
Dusty is a python application for docker based environment management.  It is built in two parts, a client and a daemon.  The daemon is a single threaded python process that should run as root.  The client is a python command line interface that interacts with both the daemon and your docker containers.

Dusty runs using a set of specs. There are four core concepts in these specs:

    1. Bundles - high level sets of functionality. These will consist of a list of apps.  Dusty will configure to run a set of bundles.
    2. Apps - Units of code that you own that are runnable.  These can rely on other apps, libs and services
    3. Libs - Units of code that you run but are not runnable.  Can rely on other libs
    4. Services - Units of code that are runnable and can be connected to, but you do not own

Using these four ideas as well as boot2docker, docker, docker-compose, host-files, nginx and virtualbox, Dusty will spin up / manage a set of containers that implement activated bundles

# Getting Started
Dusty has two parts the daemon (dustyd) and the client (dusty).  The daemon should run in the background or as a service as root.  You should use the client (dusty) to interact with it.

dusty has pretty robust cli help, to get started using it, type `dusty -h`.  This should display a list of usable commands.
Before doing anything else make sure you run the command `dusty setup`. This will help you configure dusty.

Once setup has been run, use `dusty bundles activate` to activate bundles for your local environment.
Finally, run `dusty up` to start your local environment.
