#!/usr/bin/env python

import sys
import pymysql.cursors
import configparser
import datetime
import json

config = configparser.ConfigParser()
config.read('config.ini')

now = datetime.datetime.now()

connection = pymysql.connect(host=config['mysql']['host'],
                             port=int(config['mysql']['port']),
                             user=config['mysql']['user'],
                             password=config['mysql']['password'],
                             db=config['mysql']['db'],
                             cursorclass=pymysql.cursors.DictCursor)

with connection.cursor() as cursor:
    sql = "SELECT id, CONCAT(year, '-', nmonth, '-', day, ' ', hours, ':', minutes) AS date, fname, sname, phone, lastcall, laststatus, needredial FROM scheduled_calls WHERE year>='{}' and nmonth>='{}' and day='{}' order by id".format(now.year, now.month, now.day + 1)
    cursor.execute(sql)
    for data in cursor.fetchall():
        print(data)
