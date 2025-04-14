import argparse
import logging
import os
from flask import Flask, request, render_template, redirect, url_for, flash, make_response
from flask_login import current_user, login_user, LoginManager, logout_user
from loguru import logger
from backend.db.Database import Database
from backend.language.LanguageManager import LanguageManager
from backend.util.RepositoryFactory import RepositoryFactory
from backend.util.Toolbox import Toolbox
from backend.internal_data.ConfigManager import ConfigManager
from backend.users.User import *
from backend.theme.ThemeManager import ThemeManager

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
logger.add("latest.log")

def read_args() -> dict:
    parser = argparse.ArgumentParser(description='TODO')
    parser.add_argument('dbhost')
    parser.add_argument('dbschema')
    parser.add_argument('dbuser')
    parser.add_argument('dbpw')
    args = vars(parser.parse_args())
    return args

class FlaskApp:
    __repositoryFactory = None
    __languageManager   = None
    __themeManager      = None
    __toolbox           = None
    __configManager     = None

    FORCE_MOBILE = False
    DEBUG        = True

    @logger.catch
    def __init__(self, dbhost=None, dbuser=None, dbpw=None, dbschema=None):
        logger.info("Starting up...")
        self.__configManager = ConfigManager()
        self._args = read_args()
        self.cachedGroups = ""

    def __setupDB(self, app: Flask) -> None:
        configDict = self.__configManager.getConfigValues(app)
        self.db = Database(host=configDict['dbhost'], user=configDict['dbuser'], password=configDict['dbpw'], database=configDict['dbschema'], pool_size=15)

    @logger.catch
    def create_app(self):
        logger.info("Creating Server...")
        self.app = Flask(__name__, static_url_path='', static_folder='static')
        self.app.jinja_env.globals['hasattr'] = hasattr
        self.app.config['SECRET_KEY'] = os.urandom(24).hex()
        if self.DEBUG:
            self.__configManager.overrideDBargs(self._args)
        self.__setupDB(self.app)
        logger.info("DB Connection established!")

        logger.info("Setting up local classes...")
        self.__repositoryFactory = RepositoryFactory(self.db)
        self.__languageManager   = LanguageManager()
        self.__themeManager      = ThemeManager()
        self.__toolbox           = Toolbox()
        logger.info("Local classes set up successfully")

        self.login_manager = LoginManager()
        self.login_manager.init_app(self.app)
        self.login_manager.login_view = 'login'

        def getLanguageValues():
            lang = request.cookies.get('language', LanguageManager.LANGUAGE_ENGLISH_ENGLISH)
            if lang not in self.__languageManager.getLanguages():
                logger.warning(
                    f"Language {lang} not supported, falling back to {LanguageManager.LANGUAGE_ENGLISH_ENGLISH}")
                lang = LanguageManager.LANGUAGE_ENGLISH_ENGLISH
            language_values = self.__languageManager.getLanguageValues(lang, self.app)
            language_codes = self.__languageManager.getLanguages()
            sorted_languages = sorted(
                language_codes,
                key=lambda code: language_values.get(f'index_Select_Language_{code}', '').lower()
            )
            language_values['sorted_languages'] = [
                {
                    'code': code,
                    'name': language_values.get(f'index_Select_Language_{code}', code)
                }
                for code in sorted_languages
            ]
            return language_values

        def getThemeValues(language_values):
            theme = request.cookies.get('theme', ThemeManager.THEME_DEFAULT)
            if theme not in self.__themeManager.getThemes():
                logger.warning(f"Theme {theme} not supported, falling back to {ThemeManager.THEME_DEFAULT}")
                theme = ThemeManager.THEME_DEFAULT
            theme_colors = self.__themeManager.getThemeValues(theme, self.app)
            theme_codes = self.__themeManager.getThemes()
            sorted_themes = sorted(
                theme_codes,
                key=lambda code: language_values.get(f'settings_themes_{code}', '').lower()
            )
            theme_colors['sorted_themes'] = [
                {
                    'code': code,
                    'name': language_values.get(f'settings_themes_{code}', code.capitalize())
                }
                for code in sorted_themes
            ]
            return theme_colors

        @self.login_manager.user_loader
        def load_user(userId):
            return self.__repositoryFactory.getUserRepository().getUserById(userId)

        @self.app.route("/")
        def index():
            language_values = getLanguageValues()
            theme_colors = getThemeValues(language_values)
            current_user_obj: User = current_user
            campsite_repository = self.__repositoryFactory.getCampsiteRepository()
            all_campsites = campsite_repository.getCampsitesAsDataObjects(self.db, self.__repositoryFactory.getCampsiteModuleRepository(), self.__repositoryFactory.getModuleRepository())
            if current_user_obj.is_authenticated:
                if current_user_obj.getRole() == "User":
                    pass
                elif current_user_obj.getRole() == "Campsite":
                    return index_campsite()
                elif current_user_obj.getRole() == "Admin":
                    return index_admin()
                else:
                    raise Exception("Unknown user role")
            return render_template("index.html", allCampsites=all_campsites, languageValues=language_values, theme_colors=theme_colors)

        def index_campsite():
            language_values = getLanguageValues()
            theme_colors = getThemeValues(language_values)
            return render_template("campsite_detail.html", languageValues=language_values, theme_colors=theme_colors)

        def index_admin():
            language_values = getLanguageValues()
            theme_colors = getThemeValues(language_values)
            return render_template("index_admin.html", languageValues=language_values, theme_colors=theme_colors)

        @self.app.route("/set_language/<lang>", methods=['GET'])
        def set_language(lang):
            if lang in self.__languageManager.getLanguages():
                response = make_response(redirect(request.referrer or url_for('index')))
                response.set_cookie('language', lang, max_age=60 * 60 * 24 * 30)
                return response
            else:
                flash('Language not supported')
                return redirect(url_for('index'))

        @self.app.route("/set_theme/<theme>", methods=['GET'])
        def set_theme(theme):
            if theme in self.__themeManager.getThemes():
                response = make_response(redirect(request.referrer or url_for('index')))
                response.set_cookie('theme', theme, max_age=60 * 60 * 24 * 30)
                return response
            else:
                flash('Theme not supported')
                return redirect(url_for('index'))

        @self.app.route("/login", methods=['GET', 'POST'])
        def login():
            language_values = getLanguageValues()
            theme_colors = getThemeValues(language_values)
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
            return render_template('login.html', languageValues=language_values, theme_colors=theme_colors)

        @self.app.route('/register', methods=['GET', 'POST'])
        def register():
            language_values = getLanguageValues()
            theme_colors = getThemeValues(language_values)
            if current_user.is_authenticated:
                return redirect(url_for('index'))
            if request.method == 'POST':
                role = "User"
                username = request.form.get('username')
                email = request.form.get('email')
                password_unhashed = request.form.get('password')
                firstname = request.form.get('first_name')
                lastname = request.form.get('last_name')
                birthday_day = request.form.get('birth_day')
                birthday_month = request.form.get('birth_month')
                birthday_year = request.form.get('birth_year')
                country = request.form.get('country')
                city = request.form.get('city')
                postcode = request.form.get('zip_code')
                street_name = request.form.get('street')
                house_number = request.form.get('house_number')
                err = ""
                err += validateUsername(username)
                err += validate_email(email)
                err += validate_password(password_unhashed)
                err += validate_role(role)
                if err != "":
                    flash(err)
                    return make_response('', 400)
                user_object = User()
                user_object.setUsername(username)
                user_object.setEmail(email)
                user_object.setFirstName(firstname)
                user_object.setLastName(lastname)
                user_object.setBirthday(f"{birthday_year}-{birthday_month}-{birthday_day}")
                user_object.setAddress(street_name, house_number, city, postcode, country)
                user_object.setRole('User')
                user_with_name = self.__repositoryFactory.getUserRepository().getUserByUsername(username)
                user_with_email = self.__repositoryFactory.getUserRepository().getUserByEmail(email)
                if user_with_name:
                    flash('Username already exists.')
                    return redirect(url_for('register'))
                if user_with_email:
                    flash('Email already registered.')
                    return redirect(url_for('register'))
                try:
                    user_object.setPasswordHash(generateHashedPassword(password_unhashed))
                    user_id = self.__repositoryFactory.getUserRepository().saveUserObject(self.__repositoryFactory.getAddressRepository(), user_object)
                    user_object.setId(user_id)
                    login_user(user_object)
                    flash('Registration successful!')
                    return redirect(url_for('index'))
                except Exception as e:
                    flash(f'An error occurred during registration: {str(e)}')
                    return redirect(url_for('register'))
            return render_template('register.html', languageValues=language_values, theme_colors=theme_colors)

        @self.app.route("/campsite/<campsite_id>")
        def campsite_detail(campsite_id):
            logger.info(f"Requested campsite_id: {campsite_id} (type: {type(campsite_id)})")
            language_values = getLanguageValues()
            theme_colors = getThemeValues(language_values)
            campsite_repository = self.__repositoryFactory.getCampsiteRepository()
            all_campsites = campsite_repository.getCampsitesAsDataObjects(self.db, self.__repositoryFactory.getCampsiteModuleRepository(), self.__repositoryFactory.getModuleRepository())
            logger.info(f"All campsites: {[c['id'] for c in all_campsites]}")
            campsite = next((c for c in all_campsites if str(c["id"]) == str(campsite_id)), None)
            if campsite is None:
                logger.warning(f"Campsite with ID {campsite_id} not found in {len(all_campsites)} campsites")
                flash('Campsite not found')
                return redirect(url_for('index'))
            logger.info(f"Found campsite: {campsite['name']}")
            module_metadata = {
                "Bread": {
                    "logo": "pictogram_breadModule.png",
                    "url": f"/campsite/{campsite_id}/bread_module"
                },
                "Booking": {
                    "logo": "pictogram_bookingModule.png",
                    "url": f"/campsite/{campsite_id}/booking_module"
                }
            }
            modules = campsite["modules"] or []
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
            return render_template("campsite_detail.html", campsite=campsite, modules=enriched_modules, languageValues=language_values, theme_colors=theme_colors)

        @self.app.route("/campsite/<campsite_id>/module/<module_id>")
        def module(campsite_id, module_id):
            language_values = getLanguageValues()
            theme_colors = getThemeValues(language_values)
            module_id = 1  # todo change later
            return render_template("module.html", languageValues=language_values, theme_colors=theme_colors)

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