from flask import Flask
from app.utils import log
from app.utils import IAM

log.debug('Got IAM: {}'.format(IAM().get()))

app = Flask(__name__)
