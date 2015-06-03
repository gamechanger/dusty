#!/bin/bash
set -ex
venv_name=venv
rm -rf $venv_name
virtualenv $venv_name
python setup.py install
$venv_name/bin/pip install "git+https://github.com/pyinstaller/pyinstaller.git@12e40471c77f588ea5be352f7219c873ddaae056#egg=pyinstaller"
$venv_name/bin/pip install .
$venv_name/bin/pyinstaller -F setup/bin/dusty
$venv_name/bin/pyinstaller -F setup/bin/dustyd
echo "Binaries can be found in dist/dusty and dist/dustyd"
rm -rf $venv_name
