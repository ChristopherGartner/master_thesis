import argparse
import logging
import os

from flask import Flask, request, render_template
from loguru import logger

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
logger.add("latest.log")


def read_args():
    parser = argparse.ArgumentParser(
        description='TODO')
    parser.add_argument('dbhost')
    parser.add_argument('dbschema')
    parser.add_argument('dbuser')
    parser.add_argument('dbpw')
    args = vars(parser.parse_args())
    return args


class FlaskApp:

    @logger.catch
    def __init__(self, dbhost=None, dbuser=None, dbpw=None, dbschema=None):
        logger.info("Starting up...")

        args = read_args()
        if not dbhost is None:
            args['dbhost'] = dbhost
            args['dbuser'] = dbuser
            args['dbpw'] = dbpw
            args['dbschema'] = dbschema
        #self.db = MySQLPool(host=args['dbhost'], user=args['dbuser'], password=args['dbpw'], database=args['dbschema'],
        #                    pool_size=15)
        self.cachedGroups = ""


    def __log(self, req):
        ip = ""
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            ip = (request.environ['REMOTE_ADDR'])
        else:
            ip = (request.environ['HTTP_X_FORWARDED_FOR'])  # if behind a proxy
        logger.info(ip + " " + req.environ.get('REQUEST_URI'))



    @logger.catch
    def create_app(self):
        logger.info("Creating Server...")
        self.app = Flask(__name__, static_url_path='', static_folder='static')

        @self.app.route("/")
        def index():
            self.__log(request)
            return render_template("index.html")


        if __name__ == '__main__':
            self.app.run(host='0.0.0.0', port=9000)
        else:
            return self.app


if __name__ == '__main__':
    fa = FlaskApp()
    fa.create_app()


