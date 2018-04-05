# Changelog

## 0.7.2 (In Progress)
* **Misc**
    * Upgraded the version of GitPython that dusty is using from 1.0.1 -> 2.1.9.  This should fix an issue with how git response were being parsed, leading to dusty failing to manage its own repositories on newer Apple computers.
    * A fix to the install script that will make it install to a temp directory, then copy over the installed binary with correct permissions to the intended installation directory.
    * A more robust solution to parsing the `RepoTags` configuration for testing.

## 0.7.1 (April 14, 2016)

* **New**
    * Added `dusty doctor` command to attempt to fix some common VirtualBox networking problems
    * Added a custom 502 page for apps which use host forwarding. This lets you see the status and logs of your container while you're waiting for its HTTP service to come online
* **Misc**
    * Implemented a [networking fix](https://github.com/docker/machine/pull/3112) the Dusty team implemented in Docker Machine within Dusty
    * The daemon now raises its open file handle limit to 8192, which should prevent some OSErrors during parallelized Git operations

## 0.7.0 (February 18, 2016)

* **Breaking**
    * Dusty app and lib spec filenames must now abide by Docker image naming conventions: `[a-z0-9]+(?:[._-][a-z0-9]+)*`. Your file name must start with a number or lowercase letter, cannot have uppercase letters, and can only have `.`, `_`, and `-` as special characters.
    * Dusty requires Docker Machine 0.5.0+
* **New**
    * Added `dusty shutdown` command to shut down Dusty's virtual machine
    * Added `--only` flag to `bundles activate` which makes it easier to turn on a selection of bundles and deactivate all others
    * Added support for SCP style GitHub urls. Example: git@github.com:gamechanger/dusty.git
    * Added `image_requires_login` key to specs which can specify Docker images to pull. If set, Dusty will make sure the user is logged in to this image's repository before trying to pull the image
    * Optimized the `up` and `test` flows for some significant performance gains
    * Dusty now shows the progress of image pulls on `dusty up`
* **Misc**
    * Added support for Docker Compose 1.6
    * `dusty disk restore` now appends the `dusty-backup` suffix to the restore path if not provided, which should make the `restore` command a bit more intuitive to use
    * Host forwarding now supports multiple forwarding rules per app to the same container port for HTTP forwarding
    * Fixed a bug where intermediate containers were not removed when creating testing images
    * Revived a previous networking fix that was removed after Dusty moved to Docker Machine. This fix improves external networking performance by up to 50% for large file transfers.
    * Fixed a case sensitive bug between HFS and NFS.

## 0.6.5 (January 13, 2016)

* **Misc**
    * Dusty now recognizes if the SSH agent socket path has changed on each command and resets the value if necessary
    * Dusty is now compatible with recent versions of `docker-machine env` by passing the `--shell` flag

## 0.6.4 (November 23, 2015)

* **Misc**
    * Added support for Docker 1.9 following breaking changes to the default Docker bridge IP.
    * Test images are now automatically rebuilt when repos they depend on have new commits.
    * Fixed a bug which could prevent tests without `once` commands from running correctly.

## 0.6.3 (October 1, 2015)

* **New**
    * Dusty can now forward arbitrary TCP connections (for example, SSH) through to running containers by specifying a `type: stream` key as part of `host_forwarding` configuration in app specs. See the [SSH server app spec](https://github.com/gamechanger/dusty-example-specs/blob/master/apps/sshServer.yml) for an example.

## 0.6.2 (September 14, 2015)

* **New**
    * Host names specified in app specs (`host_forwarding.host_name`) can now be used from inside any Dusty app container - previously they only worked from the host Mac.
* **Misc**
    * The Dusty VM now reserves 10.174.249.x for NAT routing inside the VM. Previously, it reserved 10.0.2.x.

## 0.6.1 (September 9, 2015)

* **Misc**
    * Dusty now adds any known hosts specified in the `repo` field of specs to root's known host file.  Previously, users had to manually add hosts as root, or Dusty couldn't pull repos other than GitHub.
    * `dusty upgrade` will check that requirements of the new version are satisfied before completing the upgrade.
    * Assets are now persisted between restarts of the Dusty VM.

## 0.6.0 (September 8, 2015)

* **Breaking**
    * Dusty has upgraded to [Docker Machine](https://docs.docker.com/machine/)! This replaces boot2docker as the tool for managing Docker-enabled VMs. Migration help can be found [here](https://gist.github.com/jsingle/bd1d8c04f45040b24c28)
    * The setup override flag `--boot2docker_vm_memory` has been renamed to `--vm_memory`
* **New**
    * Managed repos are now updated in parallel during `dusty up` and `dusty test`.
    * New command `dusty env` can set environment variable overrides per app or service. These variables can also be read from a file, as with Docker Compose's `env_file` key.
    * New command `dusty assets` can be used to place files like private keys inside containers, without the need to keep them in version control.
* **Misc**
    * Dusty now uses the name `dustyInternalNginx` for its own nginx container to make naming conflicts less likely.

## 0.5.0 (August 25, 2015)

* **Breaking**
    * Dusty now uses NFS instead of rsync to get repository code from your host Mac to running containers.
    * The `sync` commands no longer exist, due to the move to NFS.
    * The `restart` command no longer takes a `--no-sync` flag, due to the move to NFS.
* **New**
    * Dusty now attempts to fix a known problem with boot2docker networking, resulting in up to a 10x improvement in network performance. See [this boot2docker issue](https://github.com/boot2docker/boot2docker/issues/1022) for more information.
    * Bundles can now specify services, just as they specify apps.
* **Misc**
    * `test.once` commands that fail now cause the entire test run to fail immediately.
    * When running all test suites, a tabular summary of test results is now printed at the end of the run
    * Repos specified with `https:` or `file:` now are successfully mounted to containers by Docker Compose
    * Fixed various issues with using fully specified `ssh://user@host:port/path` URLs for repos

## 0.4.0 (August 3, 2015)

* **Breaking**
    * Dusty now removes data volumes when removing containers. Containers needing to persist data should use volume mounts inside of `/persist` in the boot2docker VM.
* **New**
    * Dusty no longer requires nginx to be installed on your Mac! Dusty now runs a containerized nginx inside Docker instead. All other functionality around host forwarding is unchanged.
    * Dusty's socket location can now be customized via the `DUSTY_SOCKET_PATH` environment variable
    * Dusty will use HTTPS to clone public repos which explicitly specify in their URL to use HTTPS
    * `dusty logs` now supports a `-t` option to show timestamps on the logging output
* **Misc**
    * `dusty upgrade` will now successfully upgrade Dusty from a RC version in all cases
    * Images with an `ENTRYPOINT` defined now work correctly when used as the basis for a Dusty app
    * All apps are now run as root in-container, via `user: root` in Docker Compose
    * `dusty status` now shows the status of Dusty's nginx container and has received some performance improvements

## 0.3.0 (July 24, 2015)
* **Breaking**
    * All rsync commands which write data to the VM (sync and disk restore) now remove any files present in the destination directory but not in the source directory. This should make it easier to reason about what is on disk on the VM side of sync. However, files written into source directories at runtime will now be deleted by sync operations.
* **New**
    * `dusty upgrade` can now be used to upgrade to a release candidate

## 0.2.2 (July 14, 2015)
* **New**
    * `dusty repos manage` can now accept an `--all` flag, to have Dusty manage all overridden repos
    * `dusty restart` can now restart stopped containers.
    * `dusty upgrade` command.  This command will upgrade Dusty's version by replacing the Dusty binary
* **Misc**
    * Containers will no longer block running commands that are backgrounded in the `once` script.
    * Scripts run through `dusty scripts` may now be provided options (args starting with `-`).
    * The install script now works on OS X 10.11 El Capitan, which we have been told is Spanish for "The Capitan."
    * Dusty's plist file is now located at `/Library/LaunchDaemons/com.gamechanger.dusty.plist`.

## 0.2.1 (July 6, 2015)
* **Breaking**
    * `all` is no longer an allowed suite.name in tests.  Setting a suite's name to `all` will cause `dusty validate` to fail.
* **Misc**
    * `dusty setup` now works correctly with the updated client/daemon model.
    * `rsync` commands now run with root privileges in the boot2docker VM. This allows `dusty disk backup` to access all files persisted to the VM.

## 0.2.0 (July 6, 2015)
* **New**
    * Dusty now offers a --all option when running tests.  This will run all test suites associated with an app or lib. Also, `all` is now a reserved suite_name.
* **Misc**
    * When creating test images, logs are now streamed to the user.

## 0.1.5 (July 1, 2015)
* **New**
    * Using a config variable, Dusty now manages how large (in megabytes) to make your vm.  On each start of boot2docker, Dusty will adjust your vm's memory size.
* **Misc**
    * Install script now passes -H flag to `sudo dusty -d --preflight-only`, so that `boot2docker version` won't create `~/.boot2docker` owned by root.
    * We are now attempting to load the SSH_AUTH_SOCK, if it is not currently set, with each Dusty command. This fixes a race condition in launchd between Dusty and SSH_AUTH_SOCK.

## 0.1.4 (June 29, 2015)
* **Breaking**
    * `services` and `compose` keys in test specs are now specified at the suite level, not the test level.
* **Misc**
    * Changed test container name spaces to include suite name. This allows all test suites app or lib to run concurrently.
    * Added some additional workarounds for boot2docker 1.7

## 0.1.3 (June 25, 2015)
* **New**
    * `--repos <repos>` option added to `dusty restart` CLI command.  This will restart active containers which use the specified repos.  Using this option is mutually exclusive with specifying containers to restart.
    * `dusty disk backup <destination>` CLI command added.  This will save the contents of your VM's `/persist` directory.
    * `dusty disk restore <source>` CLI command added.  This will write to your VM's `/persist` from `<source>`.
* **Misc**
    * `dusty test [options] <service> <command [options]>` is now functioning. Previously options supplied to the command to be tested were being incorrectly applied to `dusty test`.
    * Added support for boot2docker 1.7+, which uses 64-bit Tiny Core Linux

## 0.1.2 (June 23, 2015)
* **New**
    * Commands are now placed in a file, copied over to the container and the file containing the commands is run. This allows you to use & in your commands.
* **Misc**
    * `repo` and `mount` keys in app specs are now optional
    * We have switched to using docker-compose 1.3. https://github.com/docker/compose/releases/tag/1.3.0

## 0.1.1 (June 18, 2015)
* **Breaking**
    * We have changed the types of some of the values in app, lib, and test schema.  All commands to run in the container are now lists instead of single strings.
* **New**
    * `dusty status` CLI command has been added.  This outputs a list of activated apps, libs, and services. It also informs if a container is associated with each.
* **Misc**
    * `dusty setup` now looks for your nginx config in all 3 default locations.

## 0.1.0 (June 15, 2015)
  * Initial release
