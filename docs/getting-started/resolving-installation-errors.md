# Dusty Installation Errors

When running `dusty up`, you might encounter errors related to newer versions of `boot2docker`.

## Docker Machine returns non-zero exit status 1

### Error
This presents as an error message while running `dusty up` for the first time :

```
> dusty up
Pulling latest updates for all active managed repos:
Updating managed copy of specs-repo before loading specs
Updated managed copy of <github link>
Updating managed repos
Updated managed copy of <github link>
Initializing new Dusty VM with Docker Machine
ERROR: Command '['docker-machine', 'create', '--driver', 'virtualbox', '--virtualbox-cpu-count', '-1', '--virtualbox-memory', '6144', '--virtualbox-hostonly-nictype', 'Am79C973', 'dusty']' returned non-zero exit status 1
```

### Solution
The solution is to remove the `dusty` docker-machine and downgrade your version of `boot2docker` :

```
> docker-machine rm dusty
About to remove dusty
WARNING: This action will delete both local reference and remote instance.
Are you sure? (y/n): y
Successfully removed dusty
```

```
> docker-machine create --driver virtualbox --virtualbox-cpu-count -1 --virtualbox-memory 6144 --virtualbox-hostonly-nictype Am79C973 --virtualbox-boot2docker-url https://github.com/boot2docker/boot2docker/releases/download/v18.06.1-ce/boot2docker.iso dusty
Running pre-create checks...
(dusty) Boot2Docker URL was explicitly set to "https://github.com/boot2docker/boot2docker/releases/download/v18.06.1-ce/boot2docker.iso" at create time, so Docker Machine cannot upgrade this machine to the latest version.
Creating machine...
(dusty) Boot2Docker URL was explicitly set to "https://github.com/boot2docker/boot2docker/releases/download/v18.06.1-ce/boot2docker.iso" at create time, so Docker Machine cannot upgrade this machine to the latest version.
(dusty) Downloading <local path> from https://github.com/boot2docker/boot2docker/releases/download/v18.06.1-ce/boot2docker.iso...
(dusty) 0%....10%....20%....30%....40%....50%....60%....70%....80%....90%....100%
(dusty) Creating VirtualBox VM...
(dusty) Creating SSH key...
(dusty) Starting the VM...
(dusty) Check network to re-create if needed...
(dusty) Waiting for an IP...
Waiting for machine to be running, this may take a few minutes...
Detecting operating system of created instance...
Waiting for SSH to be available...
Detecting the provisioner...
Provisioning with boot2docker...
Copying certs to the local machine directory...
Copying certs to the remote machine...
Setting Docker configuration on the remote daemon...
Checking connection to Docker...
Docker is up and running!
```

### Verify
Simply re-run `dusty up` and ensure that the process successfully starts

```
> dusty up
...
Your local environment is now started!
```

## Error configuring NFS

### Error
This presents as an error message while running `dusty up` during the `Configuring NFS` step :

```
> dusty up
Pulling latest updates for all active managed repos:
Updating managed copy of specs-repo before loading specs
Updated managed copy of <github link>
Updating managed repos
Updated managed copy of <github link>
Compiling together the assembled specs
Compiling the port specs
Compiling the nginx config
Creating setup and script bash files
Compiling docker-compose config
Saving port forwarding to hosts file
Configuring NFS
ERROR: [Errno 1] Operation not permitted: '/etc/exports'
```

### Solution
The workaround for this in defined in [Dusty Issue #680](https://github.com/gamechanger/dusty/issues/680).

```
> vim /etc/exports
# BEGIN section for Dusty
/Users/<user>/dusty-specs 192.168.99.100 -alldirs -maproot=501:20
/private/etc/dusty/repos 192.168.99.100 -alldirs -maproot=0:0
# END section for Dusty
```

**Note:** The IP address to use in the file must match your Dusty docker machine IP address. You can see the IP for Dusty's docker machine by running `docker-machine ls`.

### Verify
After saving the changes to `/etc/exports`, restart `nfsd` and re-run dusty.

```
> sudo nfsd restart && dusty up
Pulling latest updates for all active managed repos:
Updating managed copy of specs-repo before loading specs
Updated managed copy of <github link>
Updating managed repos
Updated managed copy of <github link>
Compiling together the assembled specs
Compiling the port specs
Compiling the nginx config
Creating setup and script bash files
Compiling docker-compose config
Saving port forwarding to hosts file
Configuring NFS
Saving updated nginx config to the VM
Saving Docker Compose config and starting all containers
Pulling dustyInternalNginx (nginx:1.9.3)...
...
Pulling persistent_mongo (mongo:3.0.4)...
...
Pulling flasktwo (python:2.7.10)...
...
Creating dusty_persistent_mongo_1   ... done
Creating dusty_dustyInternalNginx_1 ... done
Creating dusty_flasktwo_1           ... done
Creating dusty_flaskone_1           ... done
Your local environment is now started!
```