#!/bin/zsh
cd `dirname $0`
source switch_conda_env.sh

cd ..
python test/test_simulate_hs300.py 12
python test/test_simulate_zz500.py 12
python test/test_simulate_sz50.py 12

