# dusty
Docker-based development environment manager



# Installation


# Basics
Dusty is a python application for docker based environment management.  It is built in two parts, a client and a daemon.  The daemon is a single threaded python process that should run as root.  The client is a python command line interface that interacts with both the daemon and your docker containers.

Dusty runs using a set of specs. There are four core concepts in these specs:
*1. Bundles - high level sets of functionality. These will consist of a list of apps.  Dusty will configure to run a set of bundles.
*2. Apps - Units of code that you own that are runnable.  These can rely on other apps, libs and services
*3. Libs - Units of code that you run but are not runnable.  Can rely on other libs
*4. Services - Units of code that are runnable and can be connected to, but you do not own

Using these four ideas as well as boot2docker, docker, docker-compose, host-files, nginx and virtualbox, Dusty will spin up / manage a set of containers that implement activated bundles

# Getting Started
Dusty has two parts the daemon (dustyd) and the client (dusty).  The daemon should run in the background or as a service as root.  You should use the client (dusty) to interact with it.

dusty has pretty robuse cli help, to get started using it, type `dusty -h`.  This should display a list of usable commands.


# Important commands
`dusty up` - This is supposed to be a do-it-all command to launch your local environment.  It will ensure the services that need to be running are running, will create a spec for docker-compose and will launch all needed containers.  If you get into a dirty state, or accidentally killed some containers, `dusty up` will put you back in a good place

`dusty stop` - This command will stop all running containers launched by dusty up

`dusty bundles` - Allows you to see and manage which bundles are activated

`dusty config` - Allows you to access and modify your dusty configuration

`dusty repos` - Allows you to see and manage sourcing for needed repos

`dusty sync` - Allows you to sync code from local repo to its copy on the boot2docker vm

`dusty restart` - Allows you to restart individual docker containers

`dusty logs` - Connect to a tail -f of the logs coming from a container

`dusty shell` - Open a shell in a running dusty container

`dusty script` - Run a predefined script in a running container

`dusty cp` - Copy a file to or from a container








# Example Specs Repo
