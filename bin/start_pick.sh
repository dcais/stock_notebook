#!/bin/zsh
cd `dirname $0`
source switch_conda_env.sh

cd ..
nohup python src/pick.py 12 > pick.log&
