#!/usr/bin/env bash
set -e
venv_name=venv
rm -rf $venv_name
virtualenv $venv_name
$venv_name/bin/pip install pyinstaller==3.4
$venv_name/bin/pip install .
$venv_name/bin/pyinstaller -F --runtime-hook=setup/binary-hook.py setup/dusty.spec
echo "Binaries can now be found at dist/dusty"
rm -rf $venv_name
