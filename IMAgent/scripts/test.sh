#! /bin/bash
set -e

echo 'y'|pip uninstall IMAgent

python setup.py install

imagent -c



