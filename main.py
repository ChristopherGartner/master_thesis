import argparse
import logging

from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import current_user, login_user
from loguru import logger
from werkzeug.security import check_password_hash

from backend.authorization.User import User
from backend.db.Database import Database
from backend.language.LanguageManager import LanguageManager
from backend.util.RepositoryFactory import RepositoryFactory
from backend.util.Toolbox import Toolbox
from backend.internal_data.ConfigManager import ConfigManager
from backend.campsite.Campsite import Campsite

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
    DEBUG = True

    @logger.catch
    def __init__(self, dbhost=None, dbuser=None, dbpw=None, dbschema=None):
        logger.info("Starting up...")

        # initializing local classes
        self.__repositoryFactory = RepositoryFactory()
        self.__languageManager   = LanguageManager()
        self.__toolbox           = Toolbox()
        self.__configManager     = ConfigManager()

        self._args = read_args()

        self.cachedGroups = ""

    def __setupDB(self, app: Flask) -> None:
        configDict = self.__configManager.getConfigValues(app)

        self.db = Database(host=configDict['dbhost'], user=configDict['dbuser'], password=configDict['dbpw'], database=configDict['dbschema'],
                           pool_size=15)

    @logger.catch
    def create_app(self):
        logger.info("Creating Server...")
        self.app = Flask(__name__, static_url_path='', static_folder='static')
        if self.DEBUG: self.__configManager.overrideDBargs(self._args)
        self.__setupDB(self.app)

        @self.app.route("/")
        def index():

            campsiteRepository = self.__repositoryFactory.getCampsiteRepository()
            allCampsites = campsiteRepository.getCampsitesAsDataObjects()

            languageValues = self.__languageManager.getLanguageValues(LanguageManager.LANGUAGE_GERMAN, self.app)

            return render_template("index.html", allCampsites = allCampsites, languageValues = languageValues)

        @self.app.route("/login", methods = ['GET', 'POST'])
        def login():
            if current_user.is_authenticated:
                return redirect(url_for('index'))

            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')

                pwh = self.db.execute("SELECT password FROM users WHERE username=%s;", (username,))

                if not pwh or not check_password_hash(pwh, password):
                    flash('Invalid username or password')
                    return redirect(url_for('login'))

                user = User(self.db.execute("SELECT * FROM users WHERE username = %s;", (username, )))
                login_user(user)
                return redirect(url_for('index'))

            return render_template('login.html')

        @self.app.route("/index_user")
        def index_user():

            campsiteRepository = self.__repositoryFactory.getCampsiteRepository()
            allCampsites = campsiteRepository.getCampsites(self.db)

            return render_template("index_user.html", allCampsites = allCampsites)

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