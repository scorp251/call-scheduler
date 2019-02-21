#!/usr/bin/env python

import os
import pymysql.cursors
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

monthdict = {
                '01': 'января',
                '02': 'февраля',
                '03': 'марта',
                '04': 'апреля',
                '05': 'мая',
                '06': 'июня',
                '07': 'июля',
                '08': 'августа',
                '09': 'сентября',
                '10': 'октября',
                '11': 'ноября',
                '12': 'декабря'
            }

# Connect to the database
connection = pymysql.connect(host=config['mysql']['host'],
                             port=int(config['mysql']['port']),
                             user=config['mysql']['user'],
                             password=config['mysql']['password'],
                             db=config['mysql']['db'],
                             cursorclass=pymysql.cursors.DictCursor)


with os.popen("iconv -f cp1251 -t utf-8 " + config['general']['schedule_filename']) as stream:
    print(stream)
    counter = 0
    for line in stream.readlines():
        line = line.rstrip()
        counter += 1
        adata = line.split(';')
        # Gettin month and day
        d = adata[0].strip('"').split('-')
        year = d[0]
        month = monthdict[d[1]]
        day = int(d[2])
        # Getting hours and minutes
        d = adata[1].strip('"').split('.')
        hours = int(d[0])
        if len(d) == 1:
            minutes = 0
        else:
            minutes = int(d[1])
        if minutes > 0 and minutes < 6:
            minutes *= 10
        # Getting name
        d = adata[3].strip('"').split(',')[0].split()
        fname = ""
        sname =""
        if not len(d):
            print("Error in file on line {}: Name is empty".format(counter))
        else:
            fname = d[0]
        if len(d) > 1:
            sname = d[1]
        # Getting phone
        d = adata[4].strip('"')
        seq_type= type(d)
        phone = seq_type().join(filter(seq_type.isdigit, d))
        if len(phone) != 11:
            print("Error in file on line {}: Invalid phone number {}".format(counter, phone))
            continue
        if list(phone)[0] == '7':
            phone = '8' + phone[1:]
        if list(phone)[0] != '8':
            print("Error in file on line {}: Invalid phone number {}".format(counter, phone))
        sql = "INSERT INTO scheduled_calls (year, month, day, hours, minutes, fname, sname, phone) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(year, month, day, hours, minutes, fname, sname, phone)
#        print(sql)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
            connection.commit()
        except Exception as e:
            print('Error inserting in mysql database: {}'.format(e))

connection.close()