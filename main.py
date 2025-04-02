import argparse
import logging
import os

from flask import Flask, request, render_template, redirect, url_for, flash, make_response
from flask_login import current_user, login_user, LoginManager, logout_user, login_manager
from loguru import logger
from werkzeug.security import check_password_hash

from backend.authorization.User import User, validate_username, validate_email, validate_role, validate_password
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
        self.app.config['SECRET_KEY'] = os.urandom(24).hex()
        if self.DEBUG: self.__configManager.overrideDBargs(self._args)
        self.__setupDB(self.app)
        logger.info("DB Connection established!")

        self.login_manager = LoginManager()
        self.login_manager.init_app(self.app)
        self.login_manager.login_view = 'login'

        campsiteRepository = self.__repositoryFactory.getCampsiteRepository()
        allCampsites = campsiteRepository.getCampsitesAsDataObjects(self.db)
        languageValues = self.__languageManager.getLanguageValues(LanguageManager.LANGUAGE_GERMAN, self.app)


        @self.login_manager.user_loader
        def load_user(user_id):
            res = self.db.execute("SELECT * FROM users WHERE id = %s;", (user_id,))
            return User(res)

        @self.app.route("/")
        def index():
            if current_user.is_authenticated:
                if current_user.role == "User":
                    pass
                elif current_user.role == "Campsite":
                    return index_campsite()
                elif current_user.role == "Admin":
                    return index_admin()
                else:
                    raise Exception("Unknown user role")


            return render_template("index.html", allCampsites = allCampsites, languageValues = languageValues)

        def index_campsite():
            return render_template("index_campsite.html")

        def index_admin():
            return render_template("index_user.html")


        @self.app.route("/campsite/<camp>")
        def campsite(camp):
            campinfo=None
            for c in allCampsites:
                if c["name"] == camp:
                    campinfo = c
            if campinfo is None:
                pass #TODO falschen campnamen handeln

            return render_template("campsite.html", campsite=campinfo)



        @self.app.route("/login", methods = ['GET', 'POST'])
        def login():
            if current_user.is_authenticated:
                return redirect(url_for('index'))

            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')

                pwh = self.db.execute("SELECT passwordhash FROM users WHERE username=%s;", (username,))[0][0]

                if not pwh or not check_password_hash(pwh, password):
                    flash('Invalid username or password')
                    return redirect(url_for('login'))

                user = User(self.db.execute("SELECT * FROM users WHERE username = %s;", (username, )))
                login_user(user)
                return redirect(url_for('index'))

            return render_template('login.html')

        @self.app.route('/register', methods=['GET', 'POST'])
        def register():
            if current_user.is_authenticated:
                return redirect(url_for('index'))

            if request.method == 'POST':
                username = request.form.get('username')
                email = request.form.get('email')
                password = request.form.get('password')
                role = "User"

                err = ""
                err += validate_username(username)
                err += validate_email(email)
                err += validate_password(password)
                err += validate_role(role)
                if err != "":
                    flash(err)
                    return make_response('', 400)

                # Check if username or email already exists
                user_exists = self.db.execute("SELECT * FROM users WHERE username = %s;", (username,))
                email_exists = self.db.execute("SELECT * FROM users WHERE email = %s;", (email,))


                if user_exists:
                    flash('Username already exists.')
                    return redirect(url_for('register'))

                if email_exists:
                    flash('Email already registered.')
                    return redirect(url_for('register'))




                try:
                    new_user = User(username, email, role)
                    pwh = new_user.set_password(password)
                    self.db.execute("INSERT INTO users(username, email, passwordhash, role) VALUES(%s, %s, %s, %s);", (username, email, pwh, "User"), commit=True)
                    # Create new user
                    id = self.db.execute("SELECT id FROM users WHERE username = %s;", (username, ))[0][0]
                    new_user.id = id
                    login_user(new_user)

                    flash('Registration successful!')

                    return redirect(url_for('index'))
                except Exception as e:
                    flash(f'An error occurred during registration: {str(e)}')
                    return redirect(url_for('register'))

            return render_template('register.html')

        @self.app.route("/logout")
        def logout():
            logout_user()
            return redirect(url_for('index'))

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