#!/bin/bash



for filename in callfiles/*.call; do
    DATE=`date -d "-1 day" +"%Y-%m-%d_%H:%M:%S"`
    echo $DATE
    cat $filename
    echo
    mv $filename /var/spool/asterisk/outgoing/
    sleep 40
done
