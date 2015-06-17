# Dusty Architecture

## Client / Daemon Structure

Dusty uses a client/daemon structure, where a daemon (`dusty -d`) runs with root permissions,
and a client sends it commands over a unix socket. By default the daemon is run by a plist
`/System/Library/LaunchDaemons/org.gamechanger.dusty.plist`; the client is just run on the
command line.

## System Components

Dusty leverages several programs and system components:

 * your hosts file
 * nginx
 * docker
 * boot2docker
 * docker-compose

### Overview

Dusty will use docker-compose to stitch together and launch your apps
and services.  These run in docker containers inside your boot2docker VM.  Nginx allows
you to talk to these apps, by routing your local requests to intermediate ports on the
boot2docker VM. These map to any port on your app's docker container that your app would
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

### Nginx

Dusty writes a `dusty.conf` nginx configuration file, which is placed in a directory
that nginx includes (eg `/usr/local/etc/nginx/servers/`).

Nginx is used to route requests on your localhost to your boot2docker VM. Virtualbox
port forwarding is not used, instead the actual ip of the VM is used directly.  Ports
are mapped from an arbitrary port on your localhost (specified in your Dusty specs) to
an intermediate port on the VM (selected internally by dusty).  An example
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

#### Rsync

Docker is run on OSX via the boot2docker virtual machine (managed by virtualbox).  So docker containers are actually running on the linux virtual machine.  These containers, running Dusty apps and services, need to access code living on your mac.  One way to do this is to use a
Virtualbox shared folder; however the performance of shared folders is very poor.  As an
alternative, we use rsync to move files from your mac to the VM.

#### Persistent Data

Dusty stores persistent data in the folder `/persist` on the VM, which is symlinked to
boot2docker's persistent virtual disk.

### Docker-compose

[Docker-compose](https://docs.docker.com/compose/) is a tool for defining and runnning
multi-container applications with docker.  It's used to specify docker entrypoints, volumes,
linked containers, and more.  By using docker-compose linked containers, Dusty apps can
talk to other apps and services simply by using the names of those apps and services as
hostnames.
