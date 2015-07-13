# Changelog

## 0.2.2 (In Progress)
 * NEW: `dusty repos manage` can now accept an `--all` flag, to have Dusty manage all overridden repos
 * NEW: `dusty restart` can now restart stopped containers.
 * NEW: `dusty upgrade` command.  This command will upgrade Dusty's version by replacing the Dusty binary

 * FIXED: Containers will no longer block running commands that are backgrounded in the `once` script.
 * FIXED: Scripts run through `dusty scripts` may now be provided options (args starting with `-`).
 * FIXED: The install script now works on OS X 10.11 El Capitan, which we have been told is Spanish for "The Capitan."

 * Dusty's plist file is now located at `/Library/LaunchDaemons/com.gamechanger.dusty.plist`.

## 0.2.1 (July 6, 2015)
  * BREAKING CHANGE: `all` is no longer an allowed suite.name in tests.  Setting a suite's name to `all` will cause `dusty validate` to fail.

  * FIXED: `dusty setup` now works correctly with the updated client/daemon model.
  * FIXED: `rsync` commands now run with root privileges in the boot2docker VM. This allows `dusty disk backup` to access all files persisted to the VM.

## 0.2.0 (July 6, 2015)
  * NEW: Dusty now offers a --all option when running tests.  This will run all test suites associated with an app or lib. Also, `all` is now a reserved suite_name.

  * When creating test images, logs are now streamed to the user.

## 0.1.5 (July 1, 2015)
  * NEW: Using a config variable, Dusty now manages how large (in megabytes) to make your vm.  On each start of boot2docker, Dusty will adjust your vm's memory size.

  * FIXED: Install script now passes -H flag to `sudo dusty -d --preflight-only`, so that `boot2docker version` won't create `~/.boot2docker` owned by root.
  * FIXED: We are now attempting to load the SSH_AUTH_SOCK, if it is not currently set, with each Dusty command. This fixes a race condition in launchd between Dusty and SSH_AUTH_SOCK.

## 0.1.4 (June 29, 2015)
  * BREAKING CHANGE: `services` and `compose` keys in test specs are now specified at the suite level, not the test level.

  * FIXED: Changed test container name spaces to include suite name. This allows all test suites app or lib to run concurrently.

  * Added some additional workarounds for boot2docker 1.7

## 0.1.3 (June 25, 2015)
  * NEW: `--repos <repos>` option added to `dusty restart` CLI command.  This will restart active containers which use the specified repos.  Using this option is mutually exclusive with specifying containers to restart.
  * NEW: `dusty disk backup <destination>` CLI command added.  This will save the contents of your VM's `/persist` directory.
  * NEW: `dusty disk restore <source>` CLI command added.  This will write to your VM's `/persist` from `<source>`.

  * FIXED: `dusty test [options] <service> <command [options]>` is now functioning. Previously options supplied to the command to be tested were being incorrectly applied to `dusty test`.

  * Added support for boot2docker 1.7+, which uses 64-bit Tiny Core Linux

## 0.1.2 (June 23, 2015)
  * NEW: Commands are now placed in a file, copied over to the container and the file containing the commands is run. This allows you to use & in your commands.

  * `repo` and `mount` keys in app specs are now optional
  * We have switched to using docker-compose 1.3. https://github.com/docker/compose/releases/tag/1.3.0

## 0.1.1 (June 18, 2015)
  * BREAKING CHANGE: We have changed the types of some of the values in app, lib, and test schema.  All commands to run in the container are now lists instead of single strings.

  * NEW: `dusty status` CLI command has been added.  This outputs a list of activated apps, libs, and services. It also informs if a container is associated with each.

  * FIXED: `dusty setup` now looks for your nginx config in all 3 default locations.

## 0.1.0 (June 15, 2015)
  * Initial release
