#!/usr/bin/env bash
set -e
venv_name=venv
rm -rf $venv_name
virtualenv $venv_name
$venv_name/bin/pip install "git+https://github.com/pyinstaller/pyinstaller.git@12e40471c77f588ea5be352f7219c873ddaae056#egg=pyinstaller"
$venv_name/bin/pip install .
$venv_name/bin/pyinstaller -F --runtime-hook=setup/binary-hook.py setup/bin/dusty
echo "Binaries can now be found at dist/dusty"
rm -rf $venv_name
