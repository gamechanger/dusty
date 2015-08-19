# Changelog

## 0.4.1 (In Progress)

* **Breaking**
    * Dusty now uses NFS instead of rsync to get repository code from your host Mac to running containers.
    * The `sync` commands no longer exist, due to the move to NFS.
    * The `restart` command no longer takes a `--no-sync` flag, due to the move to NFS.
* **New**
    * Dusty now attempts to fix a known problem with boot2docker networking, resulting in up to a 10x improvement in network performance. See [this boot2docker issue](https://github.com/boot2docker/boot2docker/issues/1022) for more information.
    * Dusty bundles can now specify services, just as they specify apps
* **Misc**
    * `test.once` commands that fail now cause the entire test run to fail immediately.
    * When running all test suites, a tabular summary of test results is now printed at the end of the run

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
