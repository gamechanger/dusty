# Dusty Architecture

## Client / Daemon Structure

* Dusty uses a client/daemon structure.
* The daemon (`dusty -d`) runs with root permissions to modify the hosts file (/etc/hosts). By default, the daemon runs automatically via a plist and launchd.
* A client sends the daemon commands over a Unix socket, which defaults to `/var/run/dusty/dusty.sock`. The path to this socket may be customized by setting the `DUSTY_SOCKET_PATH` environment variable for both the daemon and the client.

## System Components

Dusty leverages several programs and system components:

 * /etc/hosts file
 * [Docker](https://www.docker.com/)
 * [boot2docker](http://boot2docker.io/) and [Virtualbox](https://www.virtualbox.org/wiki/VirtualBox)
 * [Docker Compose](https://docs.docker.com/compose/)
 * [rsync](https://rsync.samba.org/)

### Overview

Dusty has both a compile and a run step when executing its main command (`dusty up`).
The compile step uses the Dusty specs to do the following:

 * Produce /etc/hosts file mappings
 * Add mappings in an nginx config
 * Stitch together a docker-compose.yml file

During the run step Dusty does the following:

 * Ensures that the boot2docker VM (linux) is running
 * Syncs code from your mac to your boot2docker VM using rsync
 * Uses Docker Compose to launch your apps and services

![Architecture](assets/architecture.png)

### Hosts File

Your hosts file (`/etc/hosts`) is modified by Dusty so that you can use Dusty-specified
local host names.  An example addition to your hostfile:
```
# BEGIN section for Dusty
192.168.1.5 local.example-app.com
# END section for Dusty
```
This points `local.example-app.com` to your boot2docker VM, where the request is then handled
by the containerized nginx which Dusty manages inside the VM.

### nginx

Dusty runs a containerized nginx which is used to route requests from your boot2docker VM to
the appropriate application container. The config for this nginx instance is stored at
`/persist/dustyNginx/dustyNginx.conf` inside the boot2docker VM.

An example `dustyNginx.conf` is:
```
http {
     server {
         client_max_body_size 500M;
         listen 80;
         server_name local.example-app.com;
         location / {
             proxy_pass http://172.17.42.1:65000;
         }
     }
}
```

### Boot2docker Virtual Machine

Docker can be used on OSX via the boot2docker virtual machine (managed by Virtualbox).
The Docker containers and Docker daemon are actually running on this
linux virtual machine.  The docker client is run on OSX using the daemon's exposed socket.

#### Rsync

Containers started by Dusty need to access code living on your mac.
One way to do this is to use a Virtualbox shared folder. However, [the performance of shared
folders is very poor](http://mitchellh.com/comparing-filesystem-performance-in-virtual-machines).  As an alternative, we use rsync to move files from your mac to the VM.

Rsync is an open source utility that provides incremental file transfer.  In order to work, rysnc needs to be installed on both the source and destination machine. This means we need to install rysnc on our boot2docker virtual machine.  We are then able to quickly sync changed files from your local mac repos to your VM's copy of these repos. This sync happens on `up`, `restart`, and `test`.

When Dusty rsyncs, any files in the destination (typically the VM) which are not present in the source (typically your Mac) are deleted. This helps to keep the two folders consistent between the filesystems.

#### Persistent Data

Dusty stores persistent data in the `/persist` folder on the boot2docker VM, which is symlinked to
boot2docker's persistent virtual disk. All data in this location will survive stops and restarts of the VM.

### Docker Compose

Docker Compose is a tool for defining and runnning
multi-container applications with Docker.  It's used to specify Docker entrypoints, volumes,
linked containers, and more.  By using Docker Compose, specifically linked containers, Dusty apps can
talk to other apps and services by using their names as hostnames.

Docker Compose can set many other Docker options as well. For example, Dusty uses it to
forward the temporary port specified in nginx to an in-container port specified in Dusty specs.
