#!/bin/bash
set -ex
venv_name=vent
rm -rf $venv_name
virtualenv $venv_name
python setup.py install
$venv_name/bin/pip install pyinstaller
$venv_name/bin/pip install .
$venv_name/bin/pyinstaller -F setup/bin/dusty
$venv_name/pyinstaller -F setup/bin/dustyd
rm -rf $venv_name
