#!/bin/sh
filepath=$(cd "$(dirname "$0")";pwd)
filedir=$filepath"/"
echo $filepath
cd $filepath&&
cd ..&&




python agent/main/main.py -c -f agent/conf/agent.cnf&&
echo ok
