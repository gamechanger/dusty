# Dusty Cli Usage

## Options

#### -d

Runs the Dusty daemon.  This action must be performed as root.
If you use Dusty's install script, a plist will be setup to run
this daemon automatically for you.

#### -v

Prints the version of both the Dusty client and daemon

## Commands

To get more usage information, including arguments and options,
about any of these commands, use `dusty <command> -h`.

#### bundles
* `list`
* `activate`
* `deactivate`
Used to list, activate, and deactivate bundles in your specs repo.  Active
bundles will be launched when you run `dusty up`.

#### config
* `list`
* `listvalues`
* `set`
Used to edit Dusty's configuration values. These are stored in a configuration file
at `/etc/dusty/config.yml`, but you should **always** use `dusty config` to change
the configuration.

#### cp
Used to copy files to and from Dusty containers.  Containers must be running for this
to work.
Some examples:
```
dusty cp file_on_mac example_app:/path/to/dest/file
dusty cp example_app:/path/to/file /path/on/mac
dusty cp example_app_1:/path/to/file example_app_2:/path/to/dest/file
```
To move files to containers, Dusty mounts a `/cp` directory to all containers that
it runs.  It can then move files into and from containers by moving them into and
out of the mounted directory.  Files are moved to and from the exact path specified
using a `docker exec mv` command.

#### disk
* `inspect`
* `cleanup_containers`
* `cleanup_images`
Used to manage the disk usage of Dusty's docker images and containers.  These can end
up taking up a lot of space on boot2docker's virtual disk, which is 20G max (dynamically
allocated by Virtualbox).

`cleanup_containers` will remove containers created by Dusty with status "Exited".

`cleanup_images` removes all images specified in your specs repo as well as dangling
images.  It does not do so forcefully; this means that if a container is still using
one of these images, the image will not be removed.

#### dump
Used to dump state of Dusty and your system.  This is used for debugging.

#### logs
This is used to examine the logs of a running Dusty app or service.  It is just
a wrapper around the `docker logs` command.

#### repos
* `from`
* `list`
* `manage`
* `override`
* `update`
Used to manage github repositories for your apps, libs, and services, as well as the
repository for your Dusty specs.
* `manage` a repo to tell Dusty to manage it automatically for you
* `override` a repo to tell Dusty that you will be manually managing it
* Use `from` to override all repos in a given directory

#### restart
Restarts active containers associated with Dusty.  The following actions are performed:
* Sync repositories on your mac to boot2docker (using rsyinc)
* Use the `docker restart` command for each active container
* Since containers are not recreated, specified `once` commands will not be run

#### scripts
Used to run scripts, inside an app's container, that you specify in the spec for that
app.

#### setup
A command to set up several basic configuration values that Dusty needs to work.  This
command must be run before you run any other Dusty commands.  The config values promped
for are:
* mac_username
* default_specs_repo
* nginx_includes_dir
You can set these values with options passed to `dusty setup`; the prompt will be
suppressed for values that you set.  For example:
`dusty setup --default_specs_repo=github.com/gamechanger/dusty-specs` will prompt you
for `mac_username` and `nginx_includes_dir`, but will automatically set `dusty_specs_repo`.

#### shell
Drops you into a bash shell of the container of the app or service specified.  This is
just a shortcut for `docker exect -it <container-id> /bin/bash`

#### status
Lists active apps, libs, and services, and whether not there is a docker container currently
running associated with each.  Note that libs will never have an active container, since
they are just loaded inside app containers.  If an app or service is listed without an active
container, that means the container has exited since launch.  You can use `dusty logs` to
figure out why.

#### stop
Stops containers associated with active Dusty apps or services.

#### sync
Syncs specified repos from your local mac to the boot2docker VM. This will use either the
Dusty-managed repo or your overridden repo, depending on your settings.

#### test
Runs tests for apps or libs, using your spec configuration. By default, old test containers
that exists on your machine are re-used when you run `dusty test` - this keeps tests speedy.
Pass the `--recreate` flag to `dusty test` in order to recreate your docker container.

#### up
Launches active bundles, and all apps and services that they depend on.  This command is
optimized to successfully launch your system from any state, and not for speed.  The steps
that `dusty up` takes are:
* Ensure your boot2docker VM is up
* Pull your Dusty-managed repos
* Assemble your specs, based on active bundles, into configuration for your hosts file, nginx,
and Docker Compose
* Stops running Dusty containers
* Sync repos from your mac to boot2docker
* Re-create and launch your docker containers


#### validate
Validates your Dusty specs.  This will:
* Check that your specs contain required fields
* Check that apps, libs, and services referenced inside your specs are all defined in your specs
* Check that your dependency graph (of apps and libs) is cycle-free
You can optionally specify a directory to look for specs in; the default is to use whatever
directory is set to your Dusty specs repository, whether managed or overriden.
