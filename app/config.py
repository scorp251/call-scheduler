import os
import configparser

inifile = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '../config.ini')
config = configparser.ConfigParser()
config.read(inifile)
