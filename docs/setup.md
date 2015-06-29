## Setup

After you install Dusty, you should run `dusty setup` to do some
necessary configuration.

#### Username

Dusty runs some commands as this user that you specify.  Usually the default
here should be fine. Setting this to `root` is probably a **bad** idea.

#### Specs Repo

Dusty needs to know where your Dusty specs live.  You can enter a git
repository here if you want to manage them that way (recommended).  You
can also just specify a local file path.

If you're new to Dusty and would like to try things out, leave this blank
to use the example specs.

#### Tutorial

If this is your first time using Dusty, you can now run through the [tutorial.](getting-started/index.md)

## Advanced Setup

#### nginx Configuration

Dusty uses nginx to direct your local traffic.  It will write nginx configuration
files to a location that it detects is included by your `nginx.conf`.  If you've
never done any nginx configuration, and you've installed it in a standard way,
this should work seamlessly.  If there's something unusual about your setup,
Dusty will prompt you to take action.

The specific steps Dusty takes are:

* Search standard nginx config file locations ('/usr/local/nginx/conf', '/etc/nginx', '/usr/local/etc/nginx') for `nginx.conf`
* Search the first `nginx.conf` found for the `include` directive - this specifies a folder of additional nginx configuration files, which is where Dusty will write its configuration
* If you don't include any folders, Dusty will ask you to let it add `include servers/*;` to the end of your nginx config
* If no `nginx.conf` is found, Dusty will let you know.

If Dusty can't setup its nginx config automatically, you just need to run

```dusty config set nginx_includes_dir <folder>```

Where `folder` is the absolute path to a folder from which your nginx will include `.conf`
files when run.
