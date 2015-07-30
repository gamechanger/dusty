#!/usr/bin/env bash

# Check that the script is being run correctly and can find the Dusty executable

if [ -z ${VIRTUAL_ENV+x} ]; then
    echo "Cowardly refusing to run outside of a virtualenv"
    exit 1
fi

if ! which -s dusty; then
    echo "Could not locate the Dusty executable, are you in a virtualenv with Dusty installed?"
    exit 1
fi

if [ `which dusty` = '/usr/local/bin/dusty' ]; then
    echo "The located version of Dusty seems to be the installed binary, not a version from source. Make sure you're in your Dusty virtualenv."
    exit 1
fi

# Make sure the Python test requirements get installed, because setuptools makes that hard

DUSTY_BIN_PATH=`which dusty`
DUSTY_SOCKET_PATH=$TMPDIR"dusty-integration.sock"
ROOT_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )
TEMP_REQUIREMENTS_PATH=$TMPDIR"dusty-test-requirements.txt"
TEST_USER=`whoami`

TEST_PATH=$ROOT_DIR/tests/integration
if [ ! -z "$1" ]; then
    TEST_PATH=$TEST_PATH/$1
fi

echo "Ensuring Python test requirements are installed..."
pushd $ROOT_DIR > /dev/null
python -c "import requirements; f = open('$TEMP_REQUIREMENTS_PATH', 'w'); [f.write('{}\n'.format(lib)) for lib in requirements.test_requires]; f.close();"
pip install -q -r $TEMP_REQUIREMENTS_PATH

echo "Starting the Dusty daemon for integration testing, will require root privileges for this..."
sudo -E DUSTY_SOCKET_PATH=$DUSTY_SOCKET_PATH nohup $DUSTY_BIN_PATH -d --suppress-warnings > test-daemon.log 2>&1 &
DUSTYD_PID=$!
trap "sudo kill $DUSTYD_PID" EXIT
sleep 2

sudo -E DUSTY_SOCKET_PATH=$DUSTY_SOCKET_PATH DUSTY_ALLOW_INTEGRATION_TESTS=yes DUSTY_INTEGRATION_TESTS_USER=$TEST_USER nosetests -v $TEST_PATH

if [ $? -eq 0 ]; then
    echo "TESTS PASSED"
else
    echo "TESTS FAILED"
fi

popd > /dev/null
