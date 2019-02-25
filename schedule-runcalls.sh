#!/bin/bash

for filename in callfiles/*.call; do
    DATE=`date +"%Y-%m-%d_%H:%M:%S"`
    echo $DATE
    cat $filename
    echo
    /usr/bin/mv -f $filename /var/spool/asterisk/outgoing/
    sleep 40
done
