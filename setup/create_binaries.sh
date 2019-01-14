#!/usr/bin/env bash
set -e
venv_name=venv
rm -rf $venv_name
if [[ $(/usr/bin/python --version 2>&1) =~ .*2\.7.* ]]; then # --version outputs to stderr
    virtualenv --python=/usr/bin/python $venv_name
else
    virtualenv $venv_name
fi
$venv_name/bin/pip install pyinstaller==3.4
$venv_name/bin/pip install .
$venv_name/bin/pyinstaller -F --runtime-hook=setup/binary-hook.py setup/dusty.spec
echo "Binaries can now be found at dist/dusty"
rm -rf $venv_name
