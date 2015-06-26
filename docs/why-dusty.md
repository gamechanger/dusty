# Why Dusty?

We built Dusty to be a great way to run a development environment, and we've tried to learn from
the existing solutions out there and make improvements where we could. Here, we'll briefly go over
a few reasons why we think you'll love Dusty more than the alternatives.

## vs. Vagrant

[Vagrant](https://www.vagrantup.com) is a very powerful tool that makes it easy to provision a
virtual machine. Vagrant is often used in conjunction with configuration management software
like Chef or Puppet in order to coordinate state changes across many users.

Compared to Vagrant, Dusty has the following advantages:

* **Isolation**: With Docker containers, each service you run is fully isolated. If you have three versions of
Postgres running across production, Dusty can easily emulate that for you on your local environment. This would
be very difficult with most Vagrant setups.
* **Ease of Updating**: By default, Dusty makes sure it has the latest version of its specs whenever you
run `dusty up`. If someone changes a service in your stack and pushes a change to the specs, Dusty will set that up
for you automatically.
* **Efficiency**: Dusty's mix and match capability allows you to run only the apps you need at any given
time. Switching apps is very easy and supported out of the box. To do this in Vagrant would require heavy
scripting through a configuration management tool.

## vs. Docker Compose

We love [Docker Compose](https://docs.docker.com/compose/), and Dusty actually uses Compose to orchestrate
container lifecycles. By itself, however, Compose has some shortcomings that we've tried to address with Dusty.

* **OS X Support**: Using Docker on OS X introduces a virtual machine between your host OS and your containers,
and navigating that extra layer is often painful. It takes a lot of effort to see a container's web service in a
browser running on your Mac, or to get files between your Mac and the container. Dusty solves these problems (see
following section on OS X Support).
* **Simplified Specs**: Compose's specs model is fairly static. You write a large Composefile with all the containers for a
specific bundle of apps. It's difficult to share service configuration across these large files. Dusty simplifies the
specs model: each container is defined in exactly one place, then specs are stitched together at runtime based on the
dependencies for the bundles you want to run.
* **Mix and Match**: Dusty's simplified specs model makes it trivial to run exactly the containers you need and none
others. Define each container once, then tell Dusty what you want to run. It'll handle the dependency graph.

## OS X Support

Dusty delivers the power and flexibility of Docker to OS X. Here are the biggest improvements we've made
to running vanilla `boot2docker` on your Mac:

* **Port Forwarding**: Dusty uses nginx to rig up host name and port forwarding all the way from your Mac
into a running container. You define the host name, host port, and container port in the container's spec,
then Dusty does the rest at runtime.
* **rsync**: Dusty uses [rsync](https://rsync.samba.org/) for all file transfer operations between your Mac
and the `boot2docker` VM. This is [unbelievably fast](http://mitchellh.com/comparing-filesystem-performance-in-virtual-machines)
compared to VirtualBox Shared Folders, which `boot2docker` uses out of the box.
* **File Transfers**: Dusty provides the `dusty cp` command to copy files between your local filesystem and
containers. This can even copy files directly between two running containers.

## Built for Development Environments

Dusty is explicitly built to be a tool for development environments.

* **Isolated Tests**: Dusty lets you write your test command in the specs, then anyone using the specs can
run the tests with a simple `dusty test` command. You can also specify disposable service containers to
use for the tests. Getting a fresh database instance for your tests is simple.
* **Share Common Tasks**: Does your app have a complicated build process or some state that needs to be
managed through scripts? Write the script once, then everyone can use it through a `dusty scripts` command.
* **Docker Available, but Batteries Included**: Everything you can already do with Docker will work just
fine with Dusty. We've made some very common commands, like running a shell, directly available through
the Dusty CLI so you don't have to learn Docker to get started.
