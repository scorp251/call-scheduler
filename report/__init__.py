import sys
import logging
import configparser
import datetime
import json
from flask import Flask, jsonify, request, redirect, url_for
import pymysql.cursors

config = configparser.ConfigParser()
config.read('config.ini')


log = logging.getLogger(__name__)
log.setLevel('INFO')
log.propagate = False

INFO_FORMAT = '[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s'
TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S %z'
formatter = logging.Formatter(INFO_FORMAT, TIMESTAMP_FORMAT)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
log.addHandler(stream_handler)

app = Flask(__name__)

@app.route('/')
def index():
    now = datetime.datetime.now()
    connection = pymysql.connect(host=config['mysql']['host'],
                             port=int(config['mysql']['port']),
                             user=config['mysql']['user'],
                             password=config['mysql']['password'],
                             db=config['mysql']['db'],
                             cursorclass=pymysql.cursors.DictCursor)
    output=''
    with connection.cursor() as cursor:
        sql = "SELECT id, CONCAT(year, '-', nmonth, '-', day, ' ', hours, ':', minutes) AS date, fname, sname, phone, address, lastcall, laststatus, needredial FROM scheduled_calls WHERE year>='{}' and nmonth>='{}' and day='{}' order by id".format(now.year, now.month, now.day + 1)
        cursor.execute(sql)
        for data in cursor.fetchall():
            output = '{}<br>"{}";"{}";"{} {}";"{}";"{}";"{}";"{}";"{}"'.format(output, data['id'], data['date'], data['fname'], data['sname'], data['phone'], data['address'], data['lastcall'], data['laststatus'], data['needredial']) 
    return output

@app.after_request
def after_request(response):
    """ Logging after every request. """
    # This avoids the duplication of registry in the log,
    # since that 500 is already logged via @app.errorhandler.
    log.info('%s %s %s %s %s %s',
          request.remote_addr,
          request.method,
          request.scheme,
          request.full_path,
          response.status,
          response.headers['Content-Length'])
    return response
