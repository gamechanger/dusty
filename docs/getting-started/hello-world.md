# Hello World!

Remember when we ran that `dusty bundles list` command? There was a bundle called `hello-world`.
That seems like something we should probably run first. The `hello-world` bundle will run two
small Flask apps. Each Flask app will be available from a browser on your Mac, and they'll
each talk to a shared MongoDB instance.

The first step to running any bundle is to activate it:

```
> dusty bundles activate hello-world
Activated bundles hello-world
> dusty bundles list
+-------------+--------------------------------------------------------+----------+
|     Name    |                      Description                       | Enabled? |
+-------------+--------------------------------------------------------+----------+
|  fileserver |      A simple fileserver to demonstrate dusty cp       |          |
| hello-world | Hello world! Two running copies of a simple Flask app. |    X     |
+-------------+--------------------------------------------------------+----------+
```

Once the bundle is activated, you can use `dusty status` to see what apps, services, and
libs will be run with your current configuration:

```
> dusty status
+-----------------+---------+----------------------+
|       Name      |   Type  | Has Active Container |
+-----------------+---------+----------------------+
|     flaskone    |   app   |                      |
|     flasktwo    |   app   |                      |
| persistentMongo | service |                      |
+-----------------+---------+----------------------+
```

So there are the two Flask apps we talked about, plus the Mongo service. Great.

## Dusty Up

Time to run everything! Once you've activated the bundles you want, just issue
a single `dusty up` command and Dusty will take care of the rest.

```
> dusty up
A bunch of lines go here...
...
...
Your local environment is now started!
```

If we check the status again, we should see everything running. We can also
see the containers directly using `docker ps`. Keep in mind that everything
you can normally do with Docker will still work when you're using Dusty!

```
> dusty status
+-----------------+---------+----------------------+
|       Name      |   Type  | Has Active Container |
+-----------------+---------+----------------------+
|     flaskone    |   app   |          X           |
|     flasktwo    |   app   |          X           |
| persistentMongo | service |          X           |
+-----------------+---------+----------------------+
```

And now, for the final test, can we reach these apps in our browser? They make
themselves available at `local.flaskone.com` and `local.flasktwo.com`. Go ahead
and navigate to one. You should see this:

![Flask Hello World](../assets/flask-hello-world.png)

Try hitting both of the URLs. The combination of the individual and shared counter
shows that we are indeed running two apps and they are coordinating with each other
over the shared Mongo instance.

## Running Tests

Dusty specs can also define how tests are run for a given app. There is a mocked out
test case in the `flaskone` app. Let's run it now.

To see the test suites available for an app, use `dusty test`.

```
> dusty test flaskone
+------------+---------------------------------------+--------------+
| Test Suite |              Description              | Default Args |
+------------+---------------------------------------+--------------+
|    unit    | Run unit tests in their own container |              |
+------------+---------------------------------------+--------------+
```

Our `flaskone` app has a single test suite called `unit`. We can run this test in its
own isolated testing environment (spinning up its own containers both for the app code
and for any services it depends on) with a single command:

```
> dusty test flaskone unit
...
Creating testflaskone_flaskone_1...
..
----------------------------------------------------------------------
Ran 2 tests in 0.001s

OK
TESTS PASSED
```

This is a very basic illustration of the testing functionality. For more detail, see
the CLI and spec definition parts of the documentation.
