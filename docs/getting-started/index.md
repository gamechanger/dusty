# Using the Example Specs

**Before continuing, please make sure you've installed Dusty as covered
in [Installation](../installation.md).**

In this tutorial, we'll cover basic usage of Dusty using a publicly
available example specs repo. We'll also go over some of the details
of how the specs are implemented so you can see how to start
writing your own.

A [public repo with example specs](https://github.com/gamechanger/dusty-example-specs)
is used to provide the specs for this tutorial. To tell Dusty to use
this repo, you can either run `dusty setup` and leave the specs repo
field blank when prompted, or you can run the following:

```
> dusty config set specs_repo https://github.com/gamechanger/dusty-example-specs.git
> dusty repos update
```

To verify that this has worked, run `dusty bundles list`. You should see this:

```
+-------------+--------------------------------------------------------+------------+
|     Name    |                      Description                       | Activated? |
+-------------+--------------------------------------------------------+------------+
|  fileserver |      A simple fileserver to demonstrate dusty cp       |            |
| hello-world | Hello world! Two running copies of a simple Flask app. |            |
+-------------+--------------------------------------------------------+------------+
```

## Exploring the Example Specs

Now that we're using the example specs, we can run a few Dusty commands to get a feel
for what's included. We've already seen `dusty bundles list`, which shows our currently
available bundles. The bundles you have activated determines which apps and services are
run when you issue a `dusty up` command. Let's do a bit more introspection before
running anything.

Run `dusty repos list`. You should see:

```
+--------------------------------------------+---------------------+----------------+
|                 Full Name                  |      Short Name     | Local Override |
+--------------------------------------------+---------------------+----------------+
| github.com/gamechanger/dusty-example-specs | dusty-example-specs |                |
| github.com/gamechanger/dusty-flask-example | dusty-flask-example |                |
+--------------------------------------------+---------------------+----------------+
```

These are all the repos referenced in the apps and libraries in the example specs. By
default, Dusty will check out its own copy of these repos and mount them inside of
Docker containers for use. You may manage a repo yourself by overriding it, which we'll
cover now.

Let's check out our own copy of the example specs and tell Dusty to use that. This will
let us investigate what's inside of them, as well as make changes on the fly.

```
> cd ~
> git clone https://github.com:gamechanger/dusty-example-specs.git
Cloning into 'dusty-example-specs'...
```

Once we have a repo checked out locally, we can tell Dusty to use that copy by issuing
an override command:

```
> dusty repos override dusty-example-specs ~/dusty-example-specs
Locally overriding repo github.com/gamechanger/dusty-example-specs to use source at ~/dusty-example-specs
```

Our locally checked out copy should be the same as what Dusty pulled for its managed copy
a few minutes ago, so nothing should actually be different. As we go forward in the tutorial,
feel free to poke around the example specs to see how we're achieving the functionality of
our example applications.
