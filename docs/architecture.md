# Dusty Architecture

## Client / Daemon Structure

Dusty uses a client/daemon structure, where a daemon (`dusty -d`) runs with root permissions.
Dusty runs a daemon as root for a couple reasons: hosts file editing and nginx both require this.
A client sends the daemon commands over a unix socket. By default the daemon is run automatically
by a plist; the client is just run on the command line.

## System Components

Dusty leverages several programs and system components:

 * your hosts file
 * nginx
 * Docker
 * boot2docker & Virtualbox
 * Docker Compose

### Overview

Dusty will use Docker Compose to stitch together and launch your apps
and services.  These run in Docker containers inside your boot2docker VM.  nginx allows
you to talk to these apps, by routing your local requests to intermediate ports on the
boot2docker VM. These map to any port on your app's Docker container that your app would
like to use.

### Hosts File

Your hosts file (`/etc/hosts`) is modified by Dusty so that you can use Dusty-specified
local host names.  An example of the additions that Dusty makes to your hostfile is:
```
# BEGIN section for Dusty
127.0.0.1 local.example-app.com
# END section for Dusty
```
This allows you to visit `local.example-app.com` in your browser, `curl` it, etc.

### nginx

Dusty writes a `dusty.conf` nginx configuration file, which is placed in a directory
that nginx includes (e.g. `/usr/local/etc/nginx/servers/`).

nginx is used to route requests on your localhost to your boot2docker VM. Virtualbox
port forwarding is not used, instead the actual IP of the VM is used directly.  Ports
are mapped from any port on your localhost (specified in your Dusty specs) to
an intermediate port on the VM (selected internally by Dusty).  An example
`dusty.conf` is:
```
http {
     server {
         client_max_body_size 500M;
         listen 80;
         server_name local.example-app.com;
         location / {
             proxy_pass http://192.168.56.103:65000;
         }
     }
}
```

### Boot2docker Virtual Machine

Docker can be used on OSX via the boot2docker virtual machine (managed by Virtualbox).
So Docker containers, and the Docker daemon, are actually running on the
linux virtual machine.  The docker client can still be run on OSX, since the daemon's
socket is exposed.

#### Rsync

These containers, running Dusty apps and services, need to access code living on your mac.
One way to do this is to use a Virtualbox shared folder; however the performance of shared
folders is very poor.  As an alternative, we use rsync to move files from your mac to the VM.

#### Persistent Data

Dusty stores persistent data in the folder `/persist` on the VM, which is symlinked to
boot2docker's persistent virtual disk.

### Docker Compose

[Docker Compose](https://docs.docker.com/compose/) is a tool for defining and runnning
multi-container applications with Docker.  It's used to specify Docker entrypoints, volumes,
linked containers, and more.  By using Docker Compose linked containers, Dusty apps can
talk to other apps and services simply by using the names of those apps and services as
hostnames.
