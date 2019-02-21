#!/usr/bin/env python

import sys
import time
from datetime import datetime
import jwt
import requests
import json
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

service_account_id = config['yandex']['service_account_id']
key_id = config['yandex']['key_id']

def update_iam(iamfile):
    with open(config['yandex']['keyfile'], 'r') as private:
        private_key = private.read()

    now = int(time.time())
    payload = {
        'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        'iss': service_account_id,
        'iat': now,
        'exp': now + 360}

    encoded_token = jwt.encode(
	payload,
	private_key,
	algorithm='PS256',
	headers={'kid': key_id})

    token = encoded_token.decode('utf-8')

    payload = { 'jwt': token }
    headers = { 'Content-Type': 'application/json' }

    try:
        resp = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens', params=payload, headers=headers)
    except Exception as e:
        print('Error posting request: {}'.format(e))
        sys.exit(1)

    data = resp.text
    print(data)
    if resp.status_code == 200:
        iamfile.truncate(0)
        iamfile.write(data)
    else:
        print("Error recieved")
        sys.exit(0)

with open(config['yandex']['iamfile'], 'a+') as iamfile:
    iamfile.seek(0)
    try:
        iamdata = json.loads(iamfile.read())
    except Exception:
        update_iam(iamfile)
        iamfile.close()
        sys.exit(0)

    now = datetime.utcnow()

    datetime = datetime.strptime(iamdata['expiresAt'], '%Y-%m-%d' + 'T' + '%H:%M:%S' + '.' + '%f' + 'Z')
    print('IAM Key expieres in {}'.format(datetime - now))
    if datetime < now:
        print('Key expiered. Updating')
        update_iam(iamfile)
