import argparse
import logging

from flask import Flask, request, render_template
from loguru import logger

from backend.db.Database import Database
from backend.language.LanguageManager import LanguageManager
from backend.util.RepositoryFactory import RepositoryFactory
from backend.util.Toolbox import Toolbox
from backend.internal_data.ConfigManager import ConfigManager

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
logger.add("latest.log")


def read_args() -> dict:
    parser = argparse.ArgumentParser(
        description='TODO')
    parser.add_argument('dbhost')
    parser.add_argument('dbschema')
    parser.add_argument('dbuser')
    parser.add_argument('dbpw')
    args = vars(parser.parse_args())
    return args


class FlaskApp:

    __repositoryFactory = None
    __languageManager   = None
    __toolbox           = None
    __configManager     = None

    FORCE_MOBILE = False

    @logger.catch
    def __init__(self, dbhost=None, dbuser=None, dbpw=None, dbschema=None):
        logger.info("Starting up...")

        # initializing local classes
        self.__repositoryFactory = RepositoryFactory()
        self.__languageManager   = LanguageManager()
        self.__toolbox           = Toolbox()
        self.__configManager     = ConfigManager()

        args = read_args()

        self.cachedGroups = ""

    def __setupDB(self, app: Flask) -> None:
        configDict = self.__configManager.getConfigValues(app)

        self.db = Database(host=configDict['db_hostname'], user=configDict['db_username'], password=configDict['db_password'], database=configDict['db_schema'],
                           pool_size=15)

    @logger.catch
    def create_app(self):
        logger.info("Creating Server...")
        self.app = Flask(__name__, static_url_path='', static_folder='static')
        self.__setupDB(self.app)

        @self.app.route("/")
        def index() -> str:

            campsiteRepository = self.__repositoryFactory.getCampsiteRepository()
            allCampsites = campsiteRepository.getCampsitesAsDataObjects()

            languageValues = self.__languageManager.getLanguageValues(LanguageManager.LANGUAGE_GERMAN, self.app)

            return render_template("index.html", allCampsites = allCampsites, languageValues = languageValues)

        @self.app.before_request
        def before() -> None:
            self.__toolbox.logToDatabase(request, self.db)

        if __name__ == '__main__':
            self.app.run(host='0.0.0.0', port=9000)
        else:
            return self.app


if __name__ == '__main__':
    fa = FlaskApp()
    fa.create_app()


