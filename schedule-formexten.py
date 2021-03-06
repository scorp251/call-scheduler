#!/usr/bin/env python

import os
import sys
import json
import time
import hashlib
import requests
import pymysql.cursors
import configparser
import datetime
import time
from trender import TRender

config = configparser.ConfigParser()
config.read('config.ini')

folder_id=config['yandex']['folder_id']

connection = pymysql.connect(host=config['mysql']['host'],
                             port=int(config['mysql']['port']),
                             user=config['mysql']['user'],
                             password=config['mysql']['password'],
                             db=config['mysql']['db'],
                             cursorclass=pymysql.cursors.DictCursor)

def get_tts(prefix, text):
    from datetime import datetime

    with open(config['yandex']['iamfile'], 'r') as iamfile:
        try:
            iamdata = json.loads(iamfile.read())
            if 'expiresAt' not in iamdata.keys():
                raise Exception('Error in file, no "expiresAt" field found')
        except Exception as e:
            print('Cannot load IAM: {}'.format(e))
            sys.exit(1)
        iamfile.close()

    now = datetime.utcnow()
    datetime = datetime.strptime(iamdata['expiresAt'], '%Y-%m-%d' + 'T' + '%H:%M:%S' + '.' + '%f' + 'Z')
    if datetime < now:
        print('IAM key expiered. Exiting.')
        sys.exit(1)
    
    IAM = iamdata['iamToken']
    
    fname = hashlib.md5(text.encode('utf-8')).hexdigest()
    if os.path.isfile(prefix + fname + '.opus'):
        return fname
    
    url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
    headers = {
        'Authorization': 'Bearer ' + IAM,
    }

    data = {
        'text': text,
        'voice': 'alyss',
        'emotion': 'good',
        'folderId': folder_id,
        'format': 'oggopus',
        'sampleRateHertz': 48000,
    }

    resp = requests.post(url, headers=headers, data=data)
    if resp.status_code != 200:
        raise RuntimeError("Invalid response received: code: %d, message: %s" % (resp.status_code, resp.text))
        sys.exit(1)
    with open(prefix + fname + '.opus', "wb") as f:
        print('Storing tts "' + text + '" in "' + prefix + fname + '.opus')
        f.write(resp.content)
        time.sleep(1)
        return fname

def create_dialplan(data):
    namefile = ''
#    nametext = data['fname'] + ' ' + data['sname'] + '.'
#    prefix = '/var/lib/asterisk/sounds/yandex/names/'
#    namefile = get_tts(prefix, nametext)

    tomorrowdate = 'завтра ' + str(data['day']) + ' ' + data['month']
    prefix = '/var/lib/asterisk/sounds/yandex/dates/'
    datefile = get_tts(prefix, tomorrowdate)

    if data['minutes'] == 0:
        data['minutes'] = 'ровно.'
    else:
        data['minutes'] = str(data['minutes']) + ' минут.'
    tomorrowtime = ' в ' + str(data['hours']) + ' часов ' + str(data['minutes'])
    prefix = '/var/lib/asterisk/sounds/yandex/times/'
    timefile = get_tts(prefix, tomorrowtime)

    addressfile=''
    addresstext = data['address']
    if(len(addresstext) > 1):
        prefix = '/var/lib/asterisk/sounds/yandex/address/'
        addressfile = get_tts(prefix, 'По адресу, г. ' + addresstext)

#    print('{} {} {}{} {}\n'.format(data['id'], nametext, tomorrowdate, tomorrowtime, addresstext))
    print('{} {}{} {}\n'.format(data['id'], tomorrowdate, tomorrowtime, addresstext))

    output = TRender('extention.tpl', path=config['general']['template_path']).render(
        {
            'cid': data['id'],
            'number': data['phone'],
            'namefile': namefile,
            'datefile': datefile,
            'timefile': timefile,
            'addressfile': addressfile
        }
        )
    f = open('{}/context-{}.conf'.format(config['general']['dialplan_files'], data['id']), 'w')
    f.write(output)
    f.close()

def create_callfiles(data):
    output = TRender('callfile.tpl', path=config['general']['template_path']).render(
    {
        'cid': data['id'],
        'phone': data['phone'],
    }
    )
    f = open('{}/{}.call'.format(config['general']['call_files'], data['id']), 'w')
    f.write(output)
    f.close()


folder = '/etc/asterisk/call-client'
for the_file in os.listdir(folder):
    file_path = os.path.join(folder, the_file)
    if the_file == "empty.conf":
        continue
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(e)

folder = '/opt/call-scheduler/callfiles'
for the_file in os.listdir(folder):
    file_path = os.path.join(folder, the_file)
    if the_file == ".gitignore":
        continue
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(e)

with connection.cursor() as cursor:
    now = datetime.datetime.now()
    tom = datetime.datetime.now() + datetime.timedelta(days=1)
    sql = "SELECT * FROM scheduled_calls WHERE lastcall IS NULL and laststatus IS NULL and year>='{}' and nmonth>='{}' and day='{}'".format(tom.year, tom.month, tom.day)
#    print(sql)
    cursor.execute(sql)
    for data in cursor.fetchall():
        print(data)
        create_dialplan(data)
        create_callfiles(data)

connection.close()

os.popen('/usr/sbin/asterisk -x "dialplan reload"')
