#!/bin/bash

cd /home/ubuntu/flaskapp/
git pull origin development
sudo service apache2 restart

date_time="`date +%H:%M:%S`"
echo $USER
echo $date_time >> o.txt
exit 0
