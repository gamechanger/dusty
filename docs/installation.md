# Installing Dusty

## Pre-Dusty Install

Make sure that Dusty can access your SSH keys for pulling down repositories:

```
ssh-add -K
  -or-
ssh-add -K <path-of-private-key>
```

`ssh-add` adds private key identities to the authentication agent, `ssh-agent`. This will allow Dusty
to pull repos using your saved SSH credentials. `<path-of-private-key>` should point at the SSH file set up
to talk to your remote git repository (GitHub for instance).

## Dusty Installation

The easiest way to install Dusty is with [Homebrew](http://brew.sh/):

```
brew cask install dusty
```

If that worked, [continue to Setup.](setup.md)

### Manual Installation

You can also install Dusty manually. First, make sure you have the following requirements installed:

 * [VirtualBox](https://www.virtualbox.org/wiki/VirtualBox)
 * [Docker Machine](https://docs.docker.com/machine/)
 * [Docker Compose](https://docs.docker.com/compose/)

These can be obtained all together from [Docker Toolbox](https://www.docker.com/docker-toolbox).

Then, run the following to download and install Dusty:

```
bash -c "`curl -L https://github.com/gamechanger/dusty/releases/download/0.7.0/install.sh`"
```

This script will install Dusty as a service and run the preflight check to ensure that all
dependencies are installed. If the script throws an error, make sure to resolve that before
continuing.
