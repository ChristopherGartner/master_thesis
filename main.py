import argparse
import logging
import os
from datetime import datetime

from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash, make_response, \
    session, json, jsonify
from flask_login import current_user, login_user, LoginManager, logout_user
from loguru import logger
from werkzeug.utils import secure_filename

from backend.campsite.Campsite import Campsite
from backend.db.Database import Database
from backend.language.LanguageManager import LanguageManager
from backend.util.RepositoryFactory import RepositoryFactory
from backend.util.Toolbox import Toolbox
from backend.internal_data.ConfigManager import ConfigManager
from backend.users.User import *
from backend.theme.ThemeManager import ThemeManager
from flask_login import login_required

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

    def load_svg(self, filename):
        with open(os.path.join(self.app.static_folder, 'images', filename), 'r') as f:
            return f.read()

    @logger.catch
    def create_app(self):
        logger.info("Creating Server...")
        self.app = Flask(__name__, static_url_path='', static_folder='static')
        self.app.jinja_env.globals['hasattr'] = hasattr
        self.app.jinja_env.globals['load_svg'] = self.load_svg
        self.app.config['SECRET_KEY'] = 'my-fixed-secret-key-12345'
        self.app.config['SESSION_PERMANENT'] = True
        self.app.config['PERMANENT_SESSION_LIFETIME'] = 3600
        self.app.config['SESSION_COOKIE_SECURE'] = False
        self.app.config['SESSION_COOKIE_HTTPONLY'] = True
        self.app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
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

        # Ensure upload folder exists
        UPLOAD_FOLDER = os.path.join(self.app.static_folder, 'Uploads', 'campsites')
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        self.app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
            if current_user.is_authenticated and current_user.getRole() == "Admin":
                theme = ThemeManager.THEME_ADMIN
                theme_colors = self.__themeManager.getThemeValues(theme, self.app)
                theme_colors['sorted_themes'] = [{
                    'code': ThemeManager.THEME_ADMIN,
                    'name': language_values.get(f'settings_themes_admin', 'Admin')
                }]
                return theme_colors

            theme = request.cookies.get('theme', ThemeManager.THEME_DEFAULT)
            if theme not in self.__themeManager.getThemes():
                logger.warning(f"Theme {theme} not supported, falling back to {ThemeManager.THEME_DEFAULT}")
                theme = ThemeManager.THEME_DEFAULT
            theme_colors = self.__themeManager.getThemeValues(theme, self.app)
            theme_codes = [code for code in self.__themeManager.getThemes() if code != ThemeManager.THEME_ADMIN]
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
            logger.info(f"Attempting to load user with ID: {userId} (type: {type(userId)})")
            try:
                userId = int(userId)
            except ValueError:
                logger.warning(f"Invalid userId format: {userId}")
                return None
            user = self.__repositoryFactory.getUserRepository().getUserById(userId)
            if user is None:
                logger.warning(f"No user found for ID: {userId}")
            else:
                logger.info(f"Loaded user: {user.getUsername()} (ID: {userId})")
            return user

        @self.app.route("/impressum")
        def impressum():
            language_values = getLanguageValues()
            theme_colors = getThemeValues(language_values)
            return render_template("impressum.html", languageValues=language_values, theme_colors=theme_colors)

        @self.app.route("/")
        def index():
            language_values = getLanguageValues()
            logger.debug(f"Language values loaded: {language_values.get('index_Campsites_NotFound', 'N/A')}")
            theme_colors = getThemeValues(language_values)
            logger.debug(f"Theme colors loaded: {theme_colors.get('primary-color', 'N/A')}")
            try:
                campsite_repository = self.__repositoryFactory.getCampsiteRepository()
                campsite_module_repository = self.__repositoryFactory.getCampsiteModuleRepository()
                module_repository = self.__repositoryFactory.getModuleRepository()
                rebuild_objects = current_user.is_authenticated and current_user.getRole() == "Admin"
                all_campsites = campsite_repository.getCampsitesAsDataObjects(
                    self.db,
                    campsite_module_repository,
                    module_repository
                )
                campsite_repository.getCampsiteMapper().getCampsiteObjects(
                    self.db,
                    campsite_module_repository,
                    module_repository,
                    rebuildObjects=True
                )
                logger.debug(f"Campsites retrieved: {len(all_campsites)} campsites")
                for campsite in all_campsites:
                    logger.debug(f"Campsite type (index): {type(campsite)}")
                    logger.debug(f"Campsite structure (index): {campsite}")
                    logger.debug(f"Campsite address (index): {getattr(campsite, 'address', 'N/A')}")
                admin_campsite_ids = []
                if current_user.is_authenticated:
                    campsite_admin_repository = self.__repositoryFactory.getCampsiteAdminRepository()
                    admin_assignments = campsite_admin_repository.getAdminsByUserId(current_user.getId())
                    admin_campsite_ids = [assignment['campsite_id'] for assignment in admin_assignments]
                    logger.debug(f"Admin campsite IDs for user {current_user.getUsername()}: {admin_campsite_ids}")
                if current_user.is_authenticated:
                    logger.debug(f"User: {current_user.getUsername()}, Role: {current_user.getRole()}")
                return render_template(
                    "index.html",
                    allCampsites=all_campsites,
                    admin_campsite_ids=admin_campsite_ids,
                    languageValues=language_values,
                    theme_colors=theme_colors
                )
            except Exception as e:
                logger.error(f"Error in index route: {str(e)}")
                flash(f"An error occurred: {str(e)}")
                return render_template(
                    "index.html",
                    allCampsites=[],
                    admin_campsite_ids=[],
                    languageValues=language_values,
                    theme_colors=theme_colors
                )

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
                logger.info("User already authenticated, redirecting to index")
                return redirect(url_for('index'))
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')
                logger.info(f"Login attempt for username: {username}")
                user = self.__repositoryFactory.getUserRepository().getUserByUsername(username)
                if user is None or not check_password_hash(user.getPasswordHash(), password):
                    logger.warning(f"Invalid username or password for username: {username}")
                    flash('Invalid username or password')
                    return redirect(url_for('login'))
                logger.info(f"User {username} authenticated, logging in")
                login_user(user, remember=True)
                logger.info(f"User {username} logged in, session: {session.get('user_id')}")
                logger.info(f"Current user after login: {current_user.is_authenticated}, ID: {current_user.getId() if current_user.is_authenticated else 'None'}")
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
                    login_user(user_object, remember=True)
                    flash('Registration successful!')
                    return redirect(url_for('index'))
                except Exception as e:
                    flash(f'An error occurred during registration: {str(e)}')
                    return redirect(url_for('register'))
            return render_template('register.html', languageValues=language_values, theme_colors=theme_colors)

        def load_svg(self, filename):
            possible_paths = [
                os.path.join(self.app.static_folder, 'Uploads', 'campsites', filename),
                os.path.join(self.app.static_folder, 'images', filename)
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        return f.read()
            return None

        @self.app.route("/edit_user", methods=['GET', 'POST'])
        @login_required
        def edit_user():
            language_values = getLanguageValues()
            theme_colors = getThemeValues(language_values)
            if request.method == 'POST':
                username = request.form.get('username')
                email = request.form.get('email')
                password = request.form.get('password')
                first_name = request.form.get('first_name')
                last_name = request.form.get('last_name')
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
                if password:
                    err += validate_password(password)
                user_with_name = self.__repositoryFactory.getUserRepository().getUserByUsername(username)
                user_with_email = self.__repositoryFactory.getUserRepository().getUserByEmail(email)
                if user_with_name and user_with_name.getId() != current_user.getId():
                    flash('Username already exists.')
                    return redirect(url_for('edit_user'))
                if user_with_email and user_with_email.getId() != current_user.getId():
                    flash('Email already registered.')
                    return redirect(url_for('edit_user'))
                if err:
                    flash(err)
                    return redirect(url_for('edit_user'))
                try:
                    user_object = current_user
                    user_object.setUsername(username)
                    user_object.setEmail(email)
                    if password:
                        user_object.setPasswordHash(generateHashedPassword(password))
                    user_object.setFirstName(first_name)
                    user_object.setLastName(last_name)
                    user_object.setBirthday(f"{birthday_year}-{birthday_month}-{birthday_day}")
                    user_object.setAddress(street_name, house_number, city, postcode, country)
                    self.__repositoryFactory.getUserRepository().updateUserObject(
                        self.__repositoryFactory.getAddressRepository(), user_object
                    )
                    flash('Profile updated successfully!')
                    return redirect(url_for('index'))
                except Exception as e:
                    flash(f'An error occurred during update: {str(e)}')
                    return redirect(url_for('edit_user'))
            return render_template(
                'edit_user.html',
                user=current_user,
                languageValues=language_values,
                theme_colors=theme_colors
            )

        @self.app.route("/edit_users")
        @login_required
        def edit_users():
            if current_user.getRole() != "Admin":
                flash('Access denied')
                return redirect(url_for('index'))
            language_values = getLanguageValues()
            theme_colors = getThemeValues(language_values)
            user_repository = self.__repositoryFactory.getUserRepository()
            users = user_repository.getUsers()
            return render_template("edit_users.html", users=users, languageValues=language_values,
                                   theme_colors=theme_colors)

        @self.app.route("/edit_user_admin/<user_id>", methods=['GET', 'POST'])
        @login_required
        def edit_user_admin(user_id):
            if current_user.getRole() != "Admin":
                flash('Access denied')
                return redirect(url_for('index'))
            language_values = getLanguageValues()
            theme_colors = getThemeValues(language_values)
            user_repository = self.__repositoryFactory.getUserRepository()
            user = user_repository.getUserById(user_id)
            if not user:
                flash('User not found')
                return redirect(url_for('edit_users'))
            if user.getAddress():
                print(f"Address - Street: {user.getAddress().getStreet()}")
                print(f"Address - House Number: {user.getAddress().getHouseNumber()}")
                print(f"Address - City: {user.getAddress().getCity()}")
                print(f"Address - Zip Code: {user.getAddress().getPostCode()}")
                print(f"Address - Country: {user.getAddress().getCountry()}")
            if request.method == 'POST':
                username = request.form.get('username')
                email = request.form.get('email')
                password = request.form.get('password')
                role = request.form.get('role')
                first_name = request.form.get('first_name')
                last_name = request.form.get('last_name')
                birthday_day = request.form.get('birth_day')
                birthday_month = request.form.get('birth_month')
                birthday_year = request.form.get('birth_year')
                country = request.form.get('country')
                city = request.form.get('city')
                postcode = request.form.get('zip_code')
                street_name = request.form.get('street')
                house_number = request.form.get('house_number')
                if city and country and city.strip().lower() == country.strip().lower():
                    logger.warning(f"City ({city}) matches country ({country}), resetting city to empty")
                    city = ''
                err = ""
                err += validateUsername(username)
                err += validate_email(email)
                if password:
                    err += validate_password(password)
                err += validate_role(role)
                try:
                    birthday_day = int(birthday_day)
                    birthday_month = int(birthday_month)
                    birthday_year = int(birthday_year)
                    if not (1 <= birthday_day <= 31):
                        err += "Day must be between 1 and 31. "
                    if not (1 <= birthday_month <= 12):
                        err += "Month must be between 1 and 12. "
                    if not (1900 <= birthday_year <= 2025):
                        err += "Year must be between 1900 and 2025. "
                except ValueError:
                    err += "Invalid date values. "
                user_with_name = user_repository.getUserByUsername(username)
                user_with_email = user_repository.getUserByEmail(email)
                if user_with_name and user_with_name.getId() != user.getId():
                    flash('Username already exists.')
                    return redirect(url_for('edit_user_admin', user_id=user_id))
                if user_with_email and user_with_email.getId() != user.getId():
                    flash('Email already registered.')
                    return redirect(url_for('edit_user_admin', user_id=user_id))
                if err:
                    flash(err)
                    return redirect(url_for('edit_user_admin', user_id=user_id))
                try:
                    user.setUsername(username)
                    user.setEmail(email)
                    if password:
                        user.setPasswordHash(generateHashedPassword(password))
                    user.setRole(role)
                    user.setFirstName(first_name)
                    user.setLastName(last_name)
                    birthday_str = f"{birthday_year}-{birthday_month:02d}-{birthday_day:02d}"
                    user.setBirthday(birthday_str)
                    user.setAddress(street_name, house_number, city, postcode, country)
                    user_repository.updateUserObject(self.__repositoryFactory.getAddressRepository(), user)
                    flash('User updated successfully!')
                    return redirect(url_for('edit_users'))
                except Exception as e:
                    flash(f'An error occurred: {str(e)}')
                    return redirect(url_for('edit_user_admin', user_id=user_id))
            return render_template("edit_user_admin.html", user=user, languageValues=language_values,
                                   theme_colors=theme_colors)

        @self.app.route("/edit_campsite/<campsite_id>", methods=['GET', 'POST'])
        @login_required
        def edit_campsite(campsite_id):
            logger.info(f"Request method: {request.method}, URL: {request.url}")
            campsite_admin_repository = self.__repositoryFactory.getCampsiteAdminRepository()
            admin_assignments = campsite_admin_repository.getAdminsByUserId(current_user.getId())
            admin_campsite_ids = [assignment['campsite_id'] for assignment in admin_assignments]
            logger.info(
                f"User {current_user.getUsername()} (Role: {current_user.getRole()}) accessing campsite {campsite_id}")
            logger.info(f"Admin campsite IDs: {admin_campsite_ids}")
            if current_user.getRole() != "Admin" and int(campsite_id) not in admin_campsite_ids:
                logger.warning(f"Access denied for user {current_user.getUsername()} to campsite {campsite_id}")
                flash('Access denied')
                return redirect(url_for('index'))
            language_values = getLanguageValues()
            theme_colors = getThemeValues(language_values)
            campsite_repository = self.__repositoryFactory.getCampsiteRepository()
            campsite = campsite_repository.getCampsiteById(
                int(campsite_id),
                self.db,
                self.__repositoryFactory.getCampsiteModuleRepository(),
                self.__repositoryFactory.getModuleRepository()
            )
            logger.info(f"Campsite retrieved: {campsite}")
            if not campsite:
                logger.warning(f"Campsite {campsite_id} not found")
                flash('Campsite not found')
                return redirect(url_for('index'))
            module_repository = self.__repositoryFactory.getModuleRepository()
            campsite_module_repository = self.__repositoryFactory.getCampsiteModuleRepository()
            user_repository = self.__repositoryFactory.getUserRepository()
            campsite_admin_repository = self.__repositoryFactory.getCampsiteAdminRepository()
            all_modules = module_repository.getModules(self.db)
            assigned_modules = campsite_module_repository.getModulesByCampsiteId(int(campsite_id), self.db)
            assigned_module_ids = [module.getId() for module in assigned_modules]
            all_users = user_repository.getUsers()
            assigned_admins = campsite_admin_repository.getAdminsByCampsiteId(int(campsite_id))
            assigned_admin_ids = [str(admin.getId()) for admin in assigned_admins]
            assigned_features = [f['id'] for f in campsite_repository.getAvailableFeatures() if
                                 campsite.getDataObject().get(f['id'])]
            available_features = campsite_repository.getAvailableFeatures()
            if request.method == 'POST':
                try:
                    name = request.form.get('name')
                    description = request.form.get('description')
                    street = request.form.get('street')
                    house_number = request.form.get('house_number')
                    city = request.form.get('city')
                    zip_code = request.form.get('zip_code')
                    country = request.form.get('country')
                    features_json = request.form.get('features', '[]')
                    logger.info(f"Received features JSON: {features_json}")
                    features = json.loads(features_json)
                    logger.info(f"Parsed features: {features}")
                    logo_path = campsite.getLogoPath()
                    if 'logo' in request.files:
                        file = request.files['logo']
                        if file and allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            file_path = os.path.join(self.app.config['UPLOAD_FOLDER'],
                                                     f"campsite_{campsite_id}_{filename}")
                            file.save(file_path)
                            logo_path = f"/Uploads/campsites/campsite_{campsite_id}_{filename}"
                    campsite.setName(name)
                    campsite.setDescription(description)
                    campsite.setAddress(street, house_number, city, zip_code, country)
                    feature_values = {f['id']: f['value'] for f in features}
                    logger.info(f"Feature values: {feature_values}")
                    logger.info("Setting feature values...")
                    campsite.setFeature_wlan(feature_values.get('wlan', False))
                    campsite.setFeature_paw(feature_values.get('paw', False))
                    campsite.setFeature_shower(feature_values.get('shower', False))
                    campsite.setFeature_playground(feature_values.get('playground', False))
                    campsite.setFeature_electricCurrent(feature_values.get('electric_current', False))
                    campsite.setFeature_parking(feature_values.get('parking', False))
                    campsite.setFeature_swimming(feature_values.get('swimming', False))
                    campsite.setFeature_fishing(feature_values.get('fishing', False))
                    logger.info("Feature values set successfully")
                    logger.info("Updating campsite in database...")
                    campsite_repository.updateCampsiteObject(
                        self.__repositoryFactory.getAddressRepository(),
                        campsite,
                        self.db,
                        logo_path
                    )
                    logger.info("Campsite updated successfully")
                    if current_user.getRole() == "Admin":
                        modules_str = request.form.get('modules', '')
                        admins_str = request.form.get('admins', '')
                        selected_module_ids = modules_str.split(',') if modules_str else []
                        selected_admin_ids = admins_str.split(',') if admins_str else []
                        campsite_module_repository.updateCampsiteModules(int(campsite_id), selected_module_ids, self.db,
                                                                         campsite_repository)
                        if admins_str:
                            campsite_admin_repository.updateCampsiteAdmins(int(campsite_id), selected_admin_ids)
                    campsite_repository.clearCache()
                    campsite_module_repository.clearCache()
                    flash('Campsite updated successfully!')
                    return redirect(url_for('index'))
                except Exception as e:
                    flash(f'An error occurred: {str(e)}')
                    return redirect(url_for('edit_campsite', campsite_id=campsite_id))
            return render_template(
                "edit_campsite.html",
                campsite=campsite,
                all_modules=all_modules,
                assigned_module_ids=assigned_module_ids,
                all_users=all_users,
                assigned_admin_ids=assigned_admin_ids,
                assigned_features=assigned_features,
                available_features=available_features,
                languageValues=language_values,
                theme_colors=theme_colors
            )

        @self.app.route("/create_campsite", methods=['GET', 'POST'])
        @login_required
        def create_campsite():
            if current_user.getRole() != "Admin":
                flash('Access denied')
                return redirect(url_for('index'))
            language_values = getLanguageValues()
            theme_colors = getThemeValues(language_values)
            campsite_repository = self.__repositoryFactory.getCampsiteRepository()
            module_repository = self.__repositoryFactory.getModuleRepository()
            campsite_module_repository = self.__repositoryFactory.getCampsiteModuleRepository()
            user_repository = self.__repositoryFactory.getUserRepository()
            campsite_admin_repository = self.__repositoryFactory.getCampsiteAdminRepository()
            all_modules = module_repository.getModules(self.db)
            all_users = user_repository.getUsers()
            available_features = campsite_repository.getAvailableFeatures()
            if request.method == 'POST':
                try:
                    name = request.form.get('name')
                    description = request.form.get('description')
                    street = request.form.get('street')
                    house_number = request.form.get('house_number')
                    city = request.form.get('city')
                    zip_code = request.form.get('zip_code')
                    country = request.form.get('country')
                    modules_str = request.form.get('modules', '')
                    admins_str = request.form.get('admins', '')
                    features_json = request.form.get('features', '[]')
                    features = json.loads(features_json)
                    selected_module_ids = modules_str.split(',') if modules_str else []
                    selected_admin_ids = admins_str.split(',') if admins_str else []
                    campsite = Campsite()
                    campsite.setName(name)
                    campsite.setDescription(description)
                    campsite.setAddress(street, house_number, city, zip_code, country)
                    campsite.setActive(True)
                    feature_values = {f['id']: f['value'] for f in features}
                    campsite.setFeature_wlan(feature_values.get('wlan', False))
                    campsite.setFeature_paw(feature_values.get('paw', False))
                    campsite.setFeature_shower(feature_values.get('shower', False))
                    campsite.setFeature_playground(feature_values.get('playground', False))
                    campsite.setFeature_electricCurrent(feature_values.get('electric_current', False))
                    campsite.setFeature_parking(feature_values.get('parking', False))
                    campsite.setFeature_swimming(feature_values.get('swimming', False))
                    campsite.setFeature_fishing(feature_values.get('fishing', False))
                    logo_path = None
                    if 'logo' in request.files:
                        file = request.files['logo']
                        if file and allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            file_path = os.path.join(self.app.config['UPLOAD_FOLDER'], f"new_campsite_{filename}")
                            file.save(file_path)
                            logo_path = f"/Uploads/campsites/new_campsite_{filename}"
                    address_repository = self.__repositoryFactory.getAddressRepository()
                    address_id = address_repository.saveAddressObject(campsite.getAddress(), self.db)
                    feature_params = (
                        campsite.getFeature_wlan(),
                        campsite.getFeature_paw(),
                        campsite.getFeature_shower(),
                        campsite.getFeature_playground(),
                        campsite.getFeature_electricCurrent(),
                        campsite.getFeature_parking(),
                        campsite.getFeature_swimming(),
                        campsite.getFeature_fishing(),
                    )
                    self.db.execute(
                        """
                        INSERT INTO campsite (
                            name, description, fk_address, isActive, logo_path,
                            feature_wlan, feature_paw, feature_shower, feature_playground, feature_electric_current, feature_parking, feature_swimming, feature_fishing
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (name, description, address_id, True, logo_path) + feature_params,
                        commit=True
                    )
                    campsite_id = self.db.execute("SELECT LAST_INSERT_ID()", commit=False)[0][0]
                    campsite.setId(campsite_id)
                    if logo_path:
                        new_logo_path = f"/Uploads/campsites/campsite_{campsite_id}_{filename}"
                        os.rename(
                            os.path.join(self.app.config['UPLOAD_FOLDER'], f"new_campsite_{filename}"),
                            os.path.join(self.app.config['UPLOAD_FOLDER'], f"campsite_{campsite_id}_{filename}")
                        )
                        self.db.execute(
                            "UPDATE campsite SET logo_path = %s WHERE id = %s",
                            (new_logo_path, campsite_id),
                            commit=True
                        )
                    campsite_module_repository.updateCampsiteModules(campsite_id, selected_module_ids, self.db,
                                                                     campsite_repository)
                    campsite_admin_repository.updateCampsiteAdmins(campsite_id, selected_admin_ids)
                    flash('Campsite created successfully!')
                    return redirect(url_for('edit_campsites'))
                except Exception as e:
                    flash(f'An error occurred: {str(e)}')
                    return redirect(url_for('create_campsite'))
            return render_template(
                "create_campsite.html",
                all_modules=all_modules,
                assigned_module_ids=[],
                all_users=all_users,
                assigned_admin_ids=[],
                available_features=available_features,
                languageValues=language_values,
                theme_colors=theme_colors
            )

        @self.app.route("/create_user", methods=['GET', 'POST'])
        @login_required
        def create_user():
            if current_user.getRole() != "Admin":
                flash('Access denied')
                return redirect(url_for('index'))
            language_values = getLanguageValues()
            theme_colors = getThemeValues(language_values)
            if request.method == 'POST':
                username = request.form.get('username')
                email = request.form.get('email')
                password_unhashed = request.form.get('password')
                role = request.form.get('role', 'User')
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
                    return redirect(url_for('create_user'))
                user_object = User()
                user_object.setUsername(username)
                user_object.setEmail(email)
                user_object.setFirstName(firstname)
                user_object.setLastName(lastname)
                user_object.setBirthday(f"{birthday_year}-{birthday_month}-{birthday_day}")
                user_object.setAddress(street_name, house_number, city, postcode, country)
                user_object.setRole(role)
                user_with_name = self.__repositoryFactory.getUserRepository().getUserByUsername(username)
                user_with_email = self.__repositoryFactory.getUserRepository().getUserByEmail(email)
                if user_with_name:
                    flash('Username already exists.')
                    return redirect(url_for('create_user'))
                if user_with_email:
                    flash('Email already registered.')
                    return redirect(url_for('create_user'))
                try:
                    user_object.setPasswordHash(generateHashedPassword(password_unhashed))
                    user_id = self.__repositoryFactory.getUserRepository().saveUserObject(self.__repositoryFactory.getAddressRepository(), user_object)
                    flash('User created successfully!')
                    return redirect(url_for('edit_users'))
                except Exception as e:
                    flash(f'An error occurred during user creation: {str(e)}')
                    return redirect(url_for('create_user'))
            return render_template('create_user.html', languageValues=language_values, theme_colors=theme_colors)

        @self.app.route("/campsite/<campsite_id>")
        def campsite_detail(campsite_id):
            logger.info(f"Requested campsite_id: {campsite_id} (type: {type(campsite_id)})")
            language_values = getLanguageValues()
            theme_colors = getThemeValues(language_values)
            campsite_repository = self.__repositoryFactory.getCampsiteRepository()
            all_campsites = campsite_repository.getCampsitesAsDataObjects(
                self.db,
                self.__repositoryFactory.getCampsiteModuleRepository(),
                self.__repositoryFactory.getModuleRepository()
            )
            logger.info(f"All campsites: {[c['id'] for c in all_campsites]}")
            campsite = next((c for c in all_campsites if str(c["id"]) == str(campsite_id)), None)
            if campsite is None:
                logger.warning(f"Campsite with ID {campsite_id} not found in {len(all_campsites)} campsites")
                flash('Campsite not found')
                return redirect(url_for('index'))
            logger.info(f"Found campsite: {campsite['name']}")
            admin_campsite_ids = []
            if current_user.is_authenticated:
                campsite_admin_repository = self.__repositoryFactory.getCampsiteAdminRepository()
                admin_assignments = campsite_admin_repository.getAdminsByUserId(current_user.getId())
                admin_campsite_ids = [assignment['campsite_id'] for assignment in admin_assignments]
                logger.debug(f"Admin campsite IDs for user {current_user.getUsername()}: {admin_campsite_ids}")
            available_features = campsite_repository.getAvailableFeatures()
            campsite_obj = campsite_repository.getCampsiteById(
                campsite['id'],
                self.db,
                self.__repositoryFactory.getCampsiteModuleRepository(),
                self.__repositoryFactory.getModuleRepository()
            )
            campsite['wlan'] = campsite_obj.getFeature_wlan()
            campsite['paw'] = campsite_obj.getFeature_paw()
            campsite['shower'] = campsite_obj.getFeature_shower()
            campsite['playground'] = campsite_obj.getFeature_playground()
            campsite['electric_current'] = campsite_obj.getFeature_electricCurrent()
            campsite['parking'] = campsite_obj.getFeature_parking()
            campsite['swimming'] = campsite_obj.getFeature_swimming()
            campsite['fishing'] = campsite_obj.getFeature_fishing()
            module_metadata = {
                "Bread": {
                    "logo": "pictogram_breadModule.svg",
                    "url": f"/campsite/{campsite_id}/module/bread_module"
                },
                "Booking": {
                    "logo": "pictogram_bookingModule.svg",
                    "url": f"/campsite/{campsite_id}/module/booking_module SLOPPY CODE: UserRepository getUserReplacementRepository() not found"
                },
                "Settings": {
                    "logo": "pictogram_settings.svg",
                    "url": "#"
                }
            }
            modules = campsite["modules"] or []
            enriched_modules = []
            for module in modules:
                module_data = module.getDataObject() if module else {}
                module_name = module_data.get("name", "")
                metadata = module_metadata.get(module_name, {})
                logo_filename = metadata.get("logo")
                logger.debug(f"Processing module: {module_name}, logo: {logo_filename}")
                if logo_filename:
                    logo_path = os.path.join(self.app.static_folder, "images", logo_filename)
                    if os.path.exists(logo_path):
                        logger.info(f"Loading pictogram: {logo_path}")
                    else:
                        logger.warning(f"Pictogram not found: {logo_path}, falling back to default")
                        logo_filename = "default_module.svg"
                    logo_content = self.load_svg(logo_filename)
                else:
                    logger.warning(f"No logo defined for module: {module_name}")
                    logo_content = None
                enriched_modules.append({
                    "id": module_data.get("id"),
                    "name": module_data.get("name"),
                    "logo": logo_content,
                    "url": metadata.get("url")
                })
            return render_template(
                "campsite_detail.html",
                campsite=campsite,
                modules=enriched_modules,
                admin_campsite_ids=admin_campsite_ids,
                languageValues=language_values,
                theme_colors=theme_colors,
                available_features=available_features
            )

        @self.app.route("/campsite/<campsite_id>/module/bread_module")
        @login_required
        def module_bread(campsite_id):
            language_values = getLanguageValues()
            theme_colors = getThemeValues(language_values)
            return render_template("module_bread.html", languageValues=language_values, theme_colors=theme_colors)

        @self.app.route("/campsite/<campsite_id>/module/bread_module/inventory")
        @login_required
        def module_bread_inventory(campsite_id):
            breads = self.db.execute("SELECT * FROM breadModuleInventory;")
            for bread in breads:
                if 'price' in bread and hasattr(bread['price'], 'to_eng_string'):
                    bread['price'] = float(bread['price'])
            return jsonify(breads)

        @self.app.route("/transactions", methods=['GET'])
        @login_required
        def transactions():
            language_values = getLanguageValues()
            theme_colors = getThemeValues(language_values)
            try:
                transaction_repository = self.__repositoryFactory.getTransactionRepository()
                campsite_repository = self.__repositoryFactory.getCampsiteRepository()
                module_repository = self.__repositoryFactory.getModuleRepository()
                from_date = request.args.get('from_date')
                to_date = request.args.get('to_date')
                sort_by = request.args.get('sort_by', 'date_desc')
                campsite_name = request.args.get('campsite')
                transactions = transaction_repository.getTransactionsByUserId(current_user.getId())
                if from_date:
                    transactions = [t for t in transactions if
                                    t['dateOfTransaction'] >= datetime.strptime(from_date, '%Y-%m-%d')]
                if to_date:
                    transactions = [t for t in transactions if
                                    t['dateOfTransaction'] <= datetime.strptime(to_date, '%Y-%m-%d')]
                filtered_transactions = []
                for transaction in transactions:
                    campsite = campsite_repository.getCampsiteById(transaction['campsite_id'], self.db,
                                                                   self.__repositoryFactory.getCampsiteModuleRepository(),
                                                                   self.__repositoryFactory.getModuleRepository())
                    module = module_repository.getModuleForModuleId(transaction['module_id'])
                    if campsite_name and campsite and campsite.getName().lower() != campsite_name.lower():
                        continue
                    transaction['campsite_name'] = campsite.getName() if campsite else 'Unknown'
                    transaction['module_name'] = module.getName() if module else 'Unknown'
                    address = campsite.getAddress() if campsite else None
                    address_str = f"{address.getStreet()} {address.getHouseNumber()}, {address.getCity()} {address.getPostCode()}, {address.getCountry()}" if address else 'Unknown'
                    transaction['campsite_details'] = {
                        'name': campsite.getName() if campsite else 'Unknown',
                        'address': address_str,
                        'description': campsite.getDescription() if campsite else 'Unknown'
                    }
                    filtered_transactions.append(transaction)
                transactions = filtered_transactions
                if sort_by == 'date_asc':
                    transactions.sort(key=lambda x: x['dateOfTransaction'])
                elif sort_by == 'price_desc':
                    transactions.sort(key=lambda x: x['price'], reverse=True)
                elif sort_by == 'price_asc':
                    transactions.sort(key=lambda x: x['price'])
                else:
                    transactions.sort(key=lambda x: x['dateOfTransaction'], reverse=True)
                total_spent = {}
                for transaction in transactions:
                    currency = transaction['moneyCurrency']
                    price = transaction['price']
                    if currency in total_spent:
                        total_spent[currency] += price
                    else:
                        total_spent[currency] = price
                return render_template(
                    "transactions.html",
                    transactions=transactions,
                    total_spent=total_spent,
                    from_date=from_date,
                    to_date=to_date,
                    sort_by=sort_by,
                    campsite=campsite_name,
                    languageValues=language_values,
                    theme_colors=theme_colors
                )
            except Exception as e:
                logger.error(f"Error in transactions route: {str(e)}")
                flash(f"An error occurred: {str(e)}")
                return render_template(
                    "transactions.html",
                    transactions=[],
                    total_spent={},
                    from_date=from_date,
                    to_date=to_date,
                    sort_by=sort_by,
                    campsite=campsite_name,
                    languageValues=language_values,
                    theme_colors=theme_colors
                )

        @self.app.route("/campsite/<campsite_id>/transactions", methods=['GET'])
        @login_required
        def campsite_transactions(campsite_id):
            if current_user.getRole() != "Admin":
                campsite_admin_repository = self.__repositoryFactory.getCampsiteAdminRepository()
                admin_assignments = campsite_admin_repository.getAdminsByUserId(current_user.getId())
                admin_campsite_ids = [assignment['campsite_id'] for assignment in admin_assignments]
                if int(campsite_id) not in admin_campsite_ids:
                    flash('Access denied')
                    return redirect(url_for('index'))
            language_values = getLanguageValues()
            theme_colors = getThemeValues(language_values)
            try:
                transaction_repository = self.__repositoryFactory.getTransactionRepository()
                campsite_repository = self.__repositoryFactory.getCampsiteRepository()
                module_repository = self.__repositoryFactory.getModuleRepository()
                user_repository = self.__repositoryFactory.getUserRepository()
                from_date = request.args.get('from_date')
                to_date = request.args.get('to_date')
                sort_by = request.args.get('sort_by', 'date_desc')
                username = request.args.get('username')
                transactionsForCampsite = transaction_repository.getTransactionsByCampsiteId(campsite_id)
                if from_date:
                    transactionsForCampsite = [t for t in transactionsForCampsite if
                                               t['dateOfTransaction'] >= datetime.strptime(from_date, '%Y-%m-%d')]
                if to_date:
                    transactionsForCampsite = [t for t in transactionsForCampsite if
                                               t['dateOfTransaction'] <= datetime.strptime(to_date, '%Y-%m-%d')]
                filtered_transactions = []
                for transaction in transactionsForCampsite:
                    campsite = campsite_repository.getCampsiteById(transaction['campsite_id'], self.db,
                                                                   self.__repositoryFactory.getCampsiteModuleRepository(),
                                                                   self.__repositoryFactory.getModuleRepository())
                    module = module_repository.getModuleForModuleId(transaction['module_id'])
                    user = user_repository.getUserById(transaction['user_id'])
                    if username and user and user.getUsername().lower() != username.lower():
                        continue
                    transaction['campsite_name'] = campsite.getName() if campsite else 'Unknown'
                    transaction['module_name'] = module.getName() if module else 'Unknown'
                    transaction['user_details'] = {
                        'username': user.getUsername() if user else 'Unknown',
                        'first_name': user.getFirstName() if user else 'Unknown',
                        'last_name': user.getLastName() if user else 'Unknown',
                        'email': user.getEmail() if user else 'Unknown'
                    }
                    filtered_transactions.append(transaction)
                transactionsForCampsite = filtered_transactions
                if sort_by == 'date_asc':
                    transactionsForCampsite.sort(key=lambda x: x['dateOfTransaction'])
                elif sort_by == 'price_desc':
                    transactionsForCampsite.sort(key=lambda x: x['price'], reverse=True)
                elif sort_by == 'price_asc':
                    transactionsForCampsite.sort(key=lambda x: x['price'])
                else:
                    transactionsForCampsite.sort(key=lambda x: x['dateOfTransaction'], reverse=True)
                total_spent = {}
                for transaction in transactionsForCampsite:
                    currency = transaction['moneyCurrency']
                    price = transaction['price']
                    if currency in total_spent:
                        total_spent[currency] += price
                    else:
                        total_spent[currency] = price
                return render_template(
                    "campsite_transactions.html",
                    transactions=transactionsForCampsite,
                    total_spent=total_spent,
                    campsite_id=campsite_id,
                    from_date=from_date,
                    to_date=to_date,
                    sort_by=sort_by,
                    username=username,
                    languageValues=language_values,
                    theme_colors=theme_colors
                )
            except Exception as e:
                logger.error(f"Error in campsite_transactions route: {str(e)}")
                flash(f"An error occurred: {str(e)}")
                return render_template(
                    "campsite_transactions.html",
                    transactions=[],
                    total_spent={},
                    campsite_id=campsite_id,
                    from_date=from_date,
                    to_date=to_date,
                    sort_by=sort_by,
                    username=username,
                    languageValues=language_values,
                    theme_colors=theme_colors
                )

        @self.app.route("/logout")
        def logout():
            logout_user()
            return redirect(url_for('index'))

        @self.app.route("/api/paypal-webhook", methods=['POST'])
        @login_required
        def paypal_webhook():
            """
            Handle PayPal webhook notifications.
            This endpoint receives webhook notifications from PayPal (or your frontend simulation).
            """
            # Get the JSON payload
            payload = request.json

            if not payload:
                logger.warning("Received empty payload")
                return jsonify({'status': 'error', 'message': 'Empty payload received'}), 400

            # Get all headers (useful for verification in production)
            headers = dict(request.headers)


            #TODO Hier jetzt noch aus payload['custom_data']['items_purchased'] das inventar aktualisieren und die gesamtsumme als transaktion für den Kunden anlegen


            # Log the received webhook
            logger.info(f"Received webhook: {payload.get('event_type', 'unknown event')}")

            # Create a timestamp for the log file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Save the full webhook to a file for debugging and record keeping
            webhook_filename = f"webhook_{timestamp}_{payload.get('id', 'unknown')}.json"
            print(payload)

            # Process different event types
            event_type = payload.get('event_type')
            #if event_type == 'PAYMENT.CAPTURE.COMPLETED':
            #    return process_payment_completed(payload)
            #elif event_type == 'PAYMENT.CAPTURE.PENDING':
            #    return process_payment_pending(payload)
            #elif event_type == 'PAYMENT.CAPTURE.REFUNDED':
            #    return process_payment_refunded(payload)
            #else:
            #    logger.warning(f"Unhandled event type: {event_type}")
            return jsonify({'status': 'success', 'message': f'Unhandled event type: {event_type}'}), 200

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