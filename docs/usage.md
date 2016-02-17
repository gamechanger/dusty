# Dusty CLI Usage

## Options

#### -d
```
Listen for user commands to Dusty

Usage:
  dusty -d [--suppress-warnings] [--preflight-only]

Options:
  --suppress-warnings  Do not display run time warnings to the client
  --preflight-only  Only run the preflight_check, then exit
```

Runs the Dusty daemon.  This action must be performed as root.
If you use Dusty's install script, a plist will be setup to run
this daemon automatically for you.

## Commands

To get more usage information, including arguments and options,
about any of these commands, use `dusty <command> -h`.

#### assets
```
Place files in Dusty containers

Assets are files to be put in containers, but which don't live in a repository.
Assets are declared in Dusty specs of apps and libraries, and their values are
managed with the CLI.

Usage:
    assets list [<app_or_lib>]
    assets read <asset_key>
    assets set <asset_key> <local_path>
    assets unset <asset_key>

Commands:
    list        List all assets that are defined in specs for active apps and libs
    read        Print the current value of an asset
    set         Associate an asset with the contents of a local file
    unset       Delete the currently registered value of an asset

Examples:
    To set the value of the asset GITHUB_KEY to the contents of ~/.ssh/id_rsa:
        dusty assets set GITHUB_KEY ~/.ssh/id_rsa
```

Assets are set to the contents of the local file - Dusty doesn't keep
them up to date with changes you make to the local file.  If you need to update
an asset, just re-run the `dusty assets set` command.

#### bundles
```
Manage application bundles known to Dusty.

A bundle represents a set of applications that are
run together. Dusty uses your activated bundles as
an entrypoint to resolve which apps and services it
needs to run as part of your environment.

You can choose which bundles are activated to customize
your environment to what you're working on at the moment.
You don't need to run your entire stack all the time!

Usage:
  bundles activate <bundle_names>...
  bundles deactivate <bundle_names>...
  bundles list

Commands:
  activate     Activate one or more bundles.
  deactivate   Deactivate one or more bundles.
  list         List all bundles and whether they are currently active.
```

#### config
```
Configure Dusty.

For a description of all available config keys,
run `config list`.

Usage:
  config list
  config listvalues
  config set <key> <value>

Commands:
  list          List all config keys with descriptions and current values.
  listvalues    List all config keys in machine-readable format.
  set           Set a string config key to a new value.
```
Used to edit Dusty's configuration values. These are stored in a configuration file
at `/etc/dusty/config.yml`, but you should **always** use `dusty config` to change
the configuration.

#### cp
```
Copy files between your local filesystem and Dusty-managed containers.
This tool also supports copying files directly between two containers.

To specify a file or directory location, either give just a path to
indicate a location on your local filesystem, or prefix a path with
`<service>:` to indicate a location inside a running container.

Usage:
  cp <source> <destination>

Examples:
  To copy a file from your local filesystem to the container of an app called `website`:
    cp /tmp/my-local-file.txt website:/tmp/file-inside-website-container.txt

  To copy a file from that same `website` container back to your local filesystem:
    cp website:/tmp/file-inside-website-container.txt /tmp/my-local-file.txt

  To copy a file from the `website` container to a different container called `api`:
    cp website:/tmp/website-file.txt api:/different/location/api-file.txt
```
To move files to containers, Dusty mounts a `/cp` directory to all containers that
it runs.  It can then move files into and from containers by moving them into and
out of the mounted directory.  Files are moved to and from the exact path specified
using a `docker exec mv` command.

#### disk
```
Basic tools for managing disk usage in the Docker VM

Usage:
  disk inspect
  disk cleanup_containers
  disk cleanup_images
  disk backup <destination>
  disk restore <source>

Commands:
  inspect             Prints VM disk usage information
  cleanup_containers  Cleans docker containers that have exited
  cleanup_images      Removes docker images that can be removed without the --force flag
  backup              Backs up the /persist directory on your Docker VM to your local file system
  restore             Restores a backed up /persist directory
```
Inspect, cleanup_containers, and cleanup_images are used to manage the disk usage of Dusty's docker
images and containers.  These can end up taking up a lot of space on the Docker VM's virtual disk,
which is 20G max (dynamically allocated by VirtualBox).  Cleanup_containers uses the `-v` flag with
`docker rm` to avoid dangling volumes.

Backup and restore are usefull for saving persistent data.  You may want to save the data and
send it to someone else, or save your data after recreating your Docker VM.

#### dump
```
Output diagnostic data, useful for filing bug reports.

Usage:
  dump

Commands:
  dump    Output diagnostic data from your system.
```
Used to dump state of Dusty and your system.  This is used for debugging.

#### env
```
Set environment variable overrides.

Environment variables specified will be added to app
and service container environments, overriding variables
specified in a `compose.env` spec (if present).

Usage:
  env list [<app_or_service>]
  env set <app_or_service> (<var_name> <value> | --file <local_file>)
  env unset <app_or_service> (--all | <var_name>)

Commands:
  list        List all environment variables and their current values.
  set         Set a variable name to a new value for the given app or service.
  unset       Unset a variable for the given app or service.
```

Environment overrides can be specified for apps and services.  These
are placed inside containers by adding them to Docker Compose's `environment`
key.  These environment changes take effect when `dusty up` is run.

Use the `--file` flag to specify a file to read the env from.  This file
should be of the same format that Docker Compose `env_file` supports.

#### logs
```
Tail out Docker logs for a container running a Dusty application
or service.

Usage:
  logs [-f] [-t] [--tail=NUM] <service>

Options:
  -f          follow log output
  -t          show timestamps
  --tail=NUM  show NUM lines from end of file
```
This is just a wrapper around the `docker logs` command.

#### repos
```
Manage repos referenced in the current Dusty specs.

By default, Dusty automatically manages the repos referenced
in your app and lib specs. This includes cloning the repo and
pulling updates from master to keep the Dusty-managed copy up-to-date.

Alternatively, you can override a repo to manage it yourself. This
is useful for actively developing apps and libs that depend on that
repo. To override a repo, use the `override` or `from` commands.

Usage:
  repos from <source_path>
  repos list
  repos manage <repo_name>
  repos override <repo_name> <source_path>
  repos update

Commands:
  from        Override all repos from a given directory
  list        Show state of all repos referenced in specs
  manage      Tell Dusty to manage a repo, removing any overrides
  override    Override a repo with a local copy that you manage
  update      Pull latest master on Dusty-managed repos
```

#### restart
```
Restart containers associated with Dusty apps or services.

Upon restart, an app container will execute the command specified
in its `commands.always` spec key. Restarting app containers will
also perform a NFS mount of repos needed for restarted containers,
using your current repo override settings.

Usage:
  restart ( --repos <repos>... | [<services>...] )

Options:
  --repos <repos>   If provided, Dusty will restart any containers
                    that are using the repos specified.
  <services>        If provided, Dusty will only restart the given
                    services. Otherwise, all currently running
                    services are restarted.
```
Restarts active containers associated with Dusty.  The following actions are performed:
* Mount with NFS the repos required for apps that are restarted
* Use the `docker restart` command for each active container
* Since containers are not recreated, specified `once` commands will not be run

#### scripts
```
Execute scripts defined in an app's spec inside a running app container.

Usage:
  scripts <app_name> [<script_name>] [<args>...]

Options:
  <args>  Arguments to pass to the script

Examples:
  To get information on all scripts available for an app called `website`:
    dusty scripts website

  To run the `rebuild` script defined inside the `website` app spec:
    dusty scripts website rebuild
```

#### setup
```
Run this command once after installation to set up
configuration values tailored to your system.

Usage:
  setup [--mac_username=<mac_username>] [--default_specs_repo=<specs_repo>]

Options:
  --mac_username=<mac_username>         User name of the primary Dusty client user. This user
                                        will own all Docker-related processes.
  --default_specs_repo=<specs_repo>     Repo where your Dusty specs are located. Dusty manages this
                                        repo for you just like other repos.
```

#### shell
```
Open a shell inside a running container. Works with Dusty
apps and services.

Usage:
  shell <service>

Example:
  To start a shell inside a container for a service named `website`:
    dusty shell website
```

#### shutdown
```
Shut down the Dusty VM.

Usage:
shutdown
```

#### status
```
Give information on activated apps, services and
libs. Will present which ones are running in a
container and name to use when calling addressing them.

Usage:
  status
```
Lists active apps, libs, and services, and whether not there is a docker container currently
running associated with each.  Note that libs will never have an active container, since
they are just loaded inside app containers.  If an app or service is listed without an active
container, that means the container has exited since launch.  You can use `dusty logs` to
figure out why.

#### stop
```
Stop containers associated with Dusty apps and services.

This does not remove the containers unless run with --rm

Usage:
  stop [--rm] [<services>...]

Options:
  --rm  remove containers
```

When used with the `--rm` flag, the `-v` flag is passed to `docker-compose rm` to avoid dangling
volumes.

#### test
```
Allow you to run tests in an isolated container for an app or a lib.
If args are passed, default arguments are dropped

Usage:
  test [options] <app_or_lib_name> [<suite_name>] [<args>...]

Options:
  <suite_name>  Name of the test suite you would like to run
                If `all` is specified, all suites in the spec will be run
  <args>        A list of arguments to be passed to the test script
  --recreate    Ensures that the testing image will be recreated
  --no-pull     Do not pull dusty managed repos from remotes.

Examples:
  To call test suite frontend with default arguments:
    dusty test web frontend
  To call test suite frontend with arguments in place of the defaults:
    dusty test web frontend /web/javascript
```
By default, old test containers
that exists on your machine are re-used when you run `dusty test` - this keeps tests speedy.
Pass the `--recreate` flag to `dusty test` in order to recreate your docker container.

#### up
```
Fully initialize all components of the Dusty system.

Up compiles your specs (subject to your activated bundles),
configures local port forwarding through your hosts file and
nginx, initializes your Docker VM and prepares it for
use by Dusty, and starts any containers specified by your
currently activated bundles.

Usage:
  up [--no-recreate] [--no-pull]

Options:
  --no-recreate   If a container already exists, do not recreate
                  it from scratch. This is faster, but containers
                  may get out of sync over time.
  --no-pull       Do not pull dusty managed repos from remotes
```
Launches active bundles, and all apps and services that they depend on.  This command is
optimized to successfully launch your system from any state, and not for speed.  The steps
that `dusty up` takes are:

 * Ensure your Docker VM is up
 * Pull your Dusty-managed repos
 * Assemble your specs, based on active bundles, into configuration for your hosts file, nginx,
and Docker Compose
 * Stops running Dusty containers, and removes them.  The `-v` flag of `docker-compose rm` is used, to avoid dangling volumes
 * Mount with NFS repos that are needed for activated containers
 * Re-create and launch your docker containers

#### upgrade
```
Upgrade Dusty's binaries

Upgrades Dusty to the specified version.  If no version is
specified, this will upgrade to the latest version.  This command
only works if Dusty is being run as a binary (as opposed to running
from source).

Usage:
  upgrade [<version>]

Options:
  <version>     If provided, this version of Dusty will be downloaded
                and used (defaults to use the most recent version)
```
This command downloads the binary from GitHub, replacing whatever binary is being used
to run the Dusty daemon.  The daemon then makes a call to `exec` to run the new binary.


#### validate
```
Validates specs to ensure that they're consistent with specifications

Usage:
  validate [<specs-path>]
```
Validates your Dusty specs.  This will:

 * Check that your specs contain required fields
 * Check that apps, libs, and services referenced inside your specs are all defined in your specs
 * Check that your dependency graph (of apps and libs) is cycle-free
You can optionally specify a directory to look for specs in; the default is to use whatever
directory is set to your Dusty specs repository, whether managed or overriden.
