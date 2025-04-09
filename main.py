import argparse
import logging
import os

from flask import Flask, request, render_template, redirect, url_for, flash, make_response
from flask_login import current_user, login_user, LoginManager, logout_user, login_manager
from loguru import logger
from werkzeug.security import check_password_hash

#from backend.authorization.UserToDelete import UserToDelete, validate_username, validate_email, validate_role, validate_password
from backend.db.Database import Database
from backend.language.LanguageManager import LanguageManager
from backend.util.RepositoryFactory import RepositoryFactory
from backend.util.Toolbox import Toolbox
from backend.internal_data.ConfigManager import ConfigManager
from backend.campsite.Campsite import Campsite
from backend.users.User import *

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

        self.__configManager = ConfigManager()

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

        logger.info("Setting up local classes...")
        # initializing local classes
        self.__repositoryFactory = RepositoryFactory(self.db)
        self.__languageManager = LanguageManager()
        self.__toolbox = Toolbox()
        logger.info("Local classes set up successfully")

        self.login_manager = LoginManager()
        self.login_manager.init_app(self.app)
        self.login_manager.login_view = 'login'

        campsiteRepository = self.__repositoryFactory.getCampsiteRepository()
        allCampsites = campsiteRepository.getCampsitesAsDataObjects(self.db, self.__repositoryFactory.getCampsiteModuleRepository(), self.__repositoryFactory.getModuleRepository())
        languageValues = self.__languageManager.getLanguageValues(LanguageManager.LANGUAGE_GERMAN, self.app)


        @self.login_manager.user_loader
        def load_user(userId):
            return self.__repositoryFactory.getUserRepository().getUserById(userId)

        @self.app.route("/")
        def index():
            currentUser: User = current_user
            campsite_repository = self.__repositoryFactory.getCampsiteRepository()
            all_campsites = campsite_repository.getCampsitesAsDataObjects(self.db, self.__repositoryFactory.getCampsiteModuleRepository(), self.__repositoryFactory.getModuleRepository())
            if currentUser.is_authenticated:
                if currentUser.getRole() == "User":
                    pass
                elif currentUser.getRole() == "Campsite":
                    return index_campsite()
                elif currentUser.getRole() == "Admin":
                    return index_admin()
                else:
                    raise Exception("Unknown user role")
            return render_template("index.html", allCampsites=all_campsites, languageValues=languageValues)

        def index_campsite():
            return render_template("campsite_detail.html")

        def index_admin():
            return render_template("index_admin.html")


        @self.app.route("/login", methods = ['GET', 'POST'])
        def login():
            if current_user.is_authenticated:
                return redirect(url_for('index'))

            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')

                user = self.__repositoryFactory.getUserRepository().getUserByUsername(username)
                if user is None or not check_password_hash(user.getPasswordHash(), password):
                    flash('Invalid username or password')
                    return redirect(url_for('login'))

                login_user(user)
                return redirect(url_for('index'))

            return render_template('login.html')

        @self.app.route('/register', methods=['GET', 'POST'])
        def register():
            if current_user.is_authenticated:
                return redirect(url_for('index'))

            if request.method == 'POST':
                role = "User"

                username         = request.form.get('username')
                email            = request.form.get('email')
                passwordUnhashed = request.form.get('password')
                firstname        = request.form.get('first_name')
                lastname         = request.form.get('last_name')

                # three fields for birthdate
                birthday_day   = request.form.get('birth_day')
                birthday_month = request.form.get('birth_month')
                birthday_year  = request.form.get('birth_year')

                country     = request.form.get('country')
                city        = request.form.get('city')
                postCode    = request.form.get('zip_code')
                streetName  = request.form.get('street')
                houseNumber = request.form.get('house_number')

                # some minor validations
                err = ""
                err += validateUsername(username)
                err += validate_email(email)
                err += validate_password(passwordUnhashed)
                err += validate_role(role)
                if err != "":
                    flash(err)
                    return make_response('', 400)

                userObject = User()
                userObject.setUsername(username)
                userObject.setEmail(email)
                userObject.setFirstName(firstname)
                userObject.setLastName(lastname)
                userObject.setBirthday(f"{birthday_year}-{birthday_month}-{birthday_day}")
                userObject.setAddress(streetName, houseNumber, city, postCode, country)
                userObject.setRole('User')

                # Check if user with given username or email exists
                userWithName  = self.__repositoryFactory.getUserRepository().getUserByUsername(username)
                userWithEmail = self.__repositoryFactory.getUserRepository().getUserByEmail(email)

                if userWithName:
                    flash('Username already exists.')
                    return redirect(url_for('register'))

                if userWithEmail:
                    flash('Email already registered.')
                    return redirect(url_for('register'))

                try:
                    userObject.setPasswordHash(generateHashedPassword(passwordUnhashed))
                    # Create new user
                    userId = self.__repositoryFactory.getUserRepository().saveUserObject(self.__repositoryFactory.getAddressRepository(), userObject)
                    userObject.setId(userId)

                    login_user(userObject)

                    flash('Registration successful!')

                    return redirect(url_for('index'))
                except Exception as e:
                    flash(f'An error occurred during registration: {str(e)}')
                    return redirect(url_for('register'))

            return render_template('register.html')

        @self.app.route("/campsite/<campsite_id>")
        def campsite_detail(campsite_id):
            logger.info(f"Requested campsite_id: {campsite_id} (type: {type(campsite_id)})")
            campsite_repository = self.__repositoryFactory.getCampsiteRepository()
            all_campsites = campsite_repository.getCampsitesAsDataObjects(self.db, self.__repositoryFactory.getCampsiteModuleRepository(), self.__repositoryFactory.getModuleRepository())
            logger.info(f"All campsites: {[c['id'] for c in all_campsites]}")
            campsite = next((c for c in all_campsites if str(c["id"]) == str(campsite_id)), None)
            if campsite is None:
                logger.warning(f"Campsite with ID {campsite_id} not found in {len(all_campsites)} campsites")
                flash('Campsite not found')
                return redirect(url_for('index'))
            logger.info(f"Found campsite: {campsite['name']}")

            # Map module names to logos and URLs (temporary hardcoded solution)
            module_metadata = {
                "bread_module": {
                    "logo": "pictogram_breadModule.png",
                    "url": f"/campsite/{campsite_id}/bread_module"
                },
                "booking_module": {
                    "logo": "pictogram_bookingModule.png",
                    "url": f"/campsite/{campsite_id}/booking_module"
                }
            }

            # Get modules from the campsite and enrich with metadata
            modules = campsite["modules"] or []  # Ensure it's not None
            enriched_modules = []
            for module in modules:
                module_data = module.getDataObject() if module else {}
                metadata = module_metadata.get(module_data.get("name", ""), {})
                enriched_modules.append({
                    "id": module_data.get("id"),
                    "name": module_data.get("name"),
                    "logo": metadata.get("logo"),
                    "url": metadata.get("url")
                })

            return render_template("campsite_detail.html", campsite=campsite, modules=enriched_modules)

        @self.app.route("/campsite/<campsite_id>/module/<module_id>")
        def module(campsite_id, module_id):
            module_id = 1 #todo change later
            return render_template("module.html")


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