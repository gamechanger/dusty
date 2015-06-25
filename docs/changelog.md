# Changelog

## 0.1.4 (In progress)


## 0.1.3 (June 25, 2015)
  * NEW: `--repos <repos>` option added to `dusty restart` CLI command.  This will restart active containers which use the specified repos.  Using this option is mutually exclusive with specifying containers to restart.
  * NEW: `dusty disk backup <destination>` CLI command added.  This will save the contents of your VM's `/persist` directory.
  * NEW: `dusty disk restore <source>` CLI command added.  This will write to your VM's `/persist` from `<source>`.

  * FIXED: bug where Dusty could not recognize test commands containing options (`dusty test <service> <command> [options]`)

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
