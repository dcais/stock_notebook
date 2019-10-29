#!/bin/zsh
cd `dirname $0`
source switch_conda_env.sh

cd ..
nohup python test/test_simulate_mine.py 12 > simulate.log&
