#!/bin/bash

pip3 install flask
pip3 install requests
pip3 install flask_restful
pip3 install pprint

ssh-keygen -f project_key -N $2

python3 load_balancer_launch.py
python3 launch_instances.py $1