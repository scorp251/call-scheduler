import os
import sys
import time
from datetime import datetime
import jwt
import requests
import json
from app.config import config
from app.utils.logger import log

class IAM(object):

    def __init__(self):
        self._service_account_id = config['yandex']['service_account_id']
        self._key_id = config['yandex']['key_id']
        self._iamfile = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            '../../' + config['yandex']['iamfile'])
        self._key = self.__readKey()
        self._IAM = self.__readIAM()

    def __get__(self, instance, owner):
        return self._IAM['iamToken']

    def __readKey(self):
        private_key = None
        keyfile =  os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            '../../' + config['yandex']['keyfile'])
        try:
            with open(keyfile, 'r') as private:
                private_key = private.read()
                private.close()
        except Exception as e:
            log.error('Cannot load private key: {}'.format(e))

        return private_key

    def __readIAM(self):
        try:
            with open(self._iamfile, 'a+') as iamfile:
                iamfile.seek(0)
                try:
                    iamdata = json.loads(iamfile.read())
                except Exception as e:      
                    log.error('Unable to parse IAM file {}'.format(e))
                    iamfile.close()
                    self.__updateIAM()
                    return None
            iamfile.close()
        except Exception as e:
            log.error('Cannot read IAM file: {}'.format(e))
            return None

        return iamdata

    def __updateIAM(self):
        self._IAM = None
        now = int(time.time())
        payload = {
            'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
            'iss': self._service_account_id,
            'iat': now,
            'exp': now + 360}

        try:
            encoded_token = jwt.encode(
                payload,
                self._key,
                algorithm='PS256',
                headers={'kid': self._key_id})
        except Exception as e:
            log.error('Cannot ancode jwt token for IAM: {}'.format(e))
            return

        token = encoded_token.decode('utf-8')

        payload = { 'jwt': token }
        headers = { 'Content-Type': 'application/json' }

        try:
            resp = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens', params=payload, headers=headers)
        except Exception as e:
            log.error('Error posting request for IAM data: {}'.format(e))
            return

        data = resp.text
        if resp.status_code == 200:
            try:
                with open(self._iamfile, 'w') as iamfile:
                    iamfile.write(data)
                iamfile.close()
            except Exception as e:
                log.error('Cannot write IAM file {}'.format(e))
        else:
            log.error('Error getting IAM data server returned status {}:{}'.format(resp.status_code, data))

        self._IAM = self.__readIAM()

    def __checkExpired(self):
        now = datetime.utcnow()
        dt = datetime.strptime(self._IAM['expiresAt'], '%Y-%m-%d' + 'T' + '%H:%M:%S' + '.' + '%f' + 'Z')
        log.debug('IAM Key expieres in {}'.format(dt - now))
        if dt < now:
            log.info('IAM key expiered. Updating')
            self.__updateIAM()

    def get(self):
        self.__checkExpired()
        return self._IAM['iamToken']
