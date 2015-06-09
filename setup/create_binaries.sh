#!/usr/bin/env bash
set -e
venv_name=venv
rm -rf $venv_name
virtualenv $venv_name
$venv_name/bin/pip install "git+https://github.com/pyinstaller/pyinstaller.git@12e40471c77f588ea5be352f7219c873ddaae056#egg=pyinstaller"
$venv_name/bin/pip install .
$venv_name/bin/pyinstaller -F setup/bin/dusty
$venv_name/bin/pyinstaller -F --hidden-import=dusty.cli setup/bin/dustyd
echo "Binaries can now be found at dist/dusty and dist/dustyd"
rm -rf $venv_name
