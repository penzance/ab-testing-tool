#!/bin/bash
export HOME=/home/vagrant
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv -a /home/vagrant/ab_testing_tool -r /home/vagrant/ab_testing_tool/ab_testing_tool/requirements/local.txt ab_testing_tool 
