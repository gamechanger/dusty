## Setup

After you install Dusty, you should run `dusty setup` to do some
necessary configuration.

#### Username

Dusty runs some commands as this user that you specify.  Usually the default
here should be fine. Setting this to `root` is probably a **bad** idea.

#### Specs Repo

Dusty needs to know where your Dusty specs live.  Use a pattern similar to:
```
repo: file:///local/repo/path
  -or-
repo: https://github.com/my-org/my-app.git
  -or-
repo: git@github.com:my-org/my-app.git
```
to specify the Dusty specs' location.

If you're new to Dusty and would like to try things out, leave this blank
to use the example specs.

#### Tutorial

If this is your first time using Dusty, you can now run through the [tutorial.](getting-started/index.md)
