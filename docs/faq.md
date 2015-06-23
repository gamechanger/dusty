# Frequently Asked Questions

### I'm having trouble running docker commands on my Mac - what gives??

If you're seeing something like:
```
$ docker ps
FATA[0000] Get http:///var/run/docker.sock/v1.18/containers/json: dial unix /var/run/docker.sock: no such file or directory. Are you trying to connect to a TLS-enabled daemon without TLS?
```

You probably just need to run `$(boot2docker shellinit)`

### How can Dusty access my private GitHub repos?

The Dusty daemon, which runs as root, manages your GitHub repos by default. 
To get permissions to clone from GitHub, the
Daemon will make use of your unprivileged user's SSH_AUTH_SOCK. This means that the daemon's
behavior using git should be the same as your user's, in terms of SSH authentication.

If you want Dusty to be
able to clone your private GitHub repos, you need to configure your standard user (whoever
your `mac_username` is set to), to be able to clone repositories without any prompt for
confirmation or password.

See [this GitHub help article](https://help.github.com/articles/generating-ssh-keys/)
for some info about setting up GitHub ssh keys.

Since the daemon has no way to accept a password via user input, if your key requires a
passphrase, you should run
```
ssh-add -K <path-of-private-key>
```
This will securely save the passphrase for that key in your Keychain.

### Why doesn't Dusty support Linux?

Dusty might be ported to Linux in the future, although we don't have concrete plans to
do so. Many of the problems Dusty solves are specific to an OSX environment, where
Docker can't run natively.

### I've read the Dusty docs, but I'd like more information!

We have a public Slack org where you can hang out with the Dusty core contributors
and other users. You can [register here](https://dusty-slackin.herokuapp.com/).

### Why is it called Dusty?

Dusty is named after [Dusty Baker](https://en.wikipedia.org/wiki/Dusty_Baker), 
baseball manager and co-inventor of the [high five](https://en.wikipedia.org/wiki/High_five).
