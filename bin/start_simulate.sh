#!/bin/zsh
cd `dirname $0`
source switch_conda_env.sh

cd ..
nohup python src/simulate.py 8 > simulate.log&
