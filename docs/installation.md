# Installing Dusty

## Requirements

You must have the following installed in order to run Dusty:

 * [VirtualBox](https://www.virtualbox.org/wiki/VirtualBox)
 * [Docker Machine](https://docs.docker.com/machine/)
 * [Docker Compose](https://docs.docker.com/compose/)

## Pre-Dusty Install

Dusty's requirements are all included in [Docker Toolbox](https://www.docker.com/toolbox).
Please install this before continuing.

```
ssh-add -K
  -or-
ssh-add -K <path-of-private-key>
```

`ssh-add` adds private key identities to the authentication agent, `ssh-agent`. This will allow Dusty
to pull repos using your saved SSH credentials. `<path-of-private-key>` should point at the SSH file set up
to talk to your remote git repository (GitHub for instance).

## Dusty Installation

To download and install Dusty, run:
```
bash -c "`curl -L https://github.com/gamechanger/dusty/releases/download/0.6.5/install.sh`"
```

This script will install Dusty as a service and run the preflight check to ensure that all
dependencies are installed. If the script throws an error, make sure to resolve that before
continuing.

If that worked, [continue to Setup.](setup.md)
