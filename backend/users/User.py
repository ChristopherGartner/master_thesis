from flask_login import UserMixin
from ..address.Address import Address
from werkzeug.security import generate_password_hash, check_password_hash

# method for validating whether username is ok or not
def validateUsername(username):
    if not (3 <= len(username) <= 50):
        return f"Username length is too short/too long: ({len(username)} Symbols)! It needs to be between 3-50 symbols!\n"
    else:
        return ""

# method for validating whether email is ok or not
def validate_email(email):
    if '@' in email and '.' in email:
        return ""
    else:
        return "Email invalid!\n"

# method for validating passwords
def validate_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long!\n"
    if not any(char.isdigit() for char in password):
        return "Password must contain at least one digit!\n"
    if not any(char.isupper() for char in password):
        return "Password must contain at least one uppercase letter!\n"
    return ""

# method for validating the roles
def validate_role(role):
    if role in ["User", "Campsite", "Admin"]:
        return ""
    else:
        return "Invalid role!\n"

def generateHashedPassword(password) -> str:
    passwordHash = generate_password_hash(password)
    return passwordHash

def checkPassword(inputPasswordHash, toCheckPasswordHash):
    return check_password_hash(inputPasswordHash, toCheckPasswordHash)

# Data class for users, now inheriting from UserMixin
class User(UserMixin):
    __id = None
    __username = None
    __email = None
    __passwordhash = None
    __role = None
    __address = None
    __firstname = None
    __lastname = None
    __birthday = None

    # Get methods
    def getId(self) -> int:
        return self.__id

    def getUsername(self) -> str:
        return self.__username

    def getEmail(self) -> str:
        return self.__email

    def getPasswordHash(self) -> str:
        return self.__passwordhash

    def getRole(self) -> str:
        return self.__role

    def getAddress(self) -> Address:
        return self.__address

    def getFirstName(self) -> str:
        return self.__firstname

    def getLastName(self) -> str:
        return self.__lastname

    def getBirthday(self) -> str:
        return self.__birthday

    # Set methods
    def setId(self, id) -> None:
        self.__id = int(id) if id is not None else None

    def setUsername(self, username) -> None:
        self.__username = username

    def setEmail(self, email) -> None:
        self.__email = email

    def setPasswordHash(self, passwordHash) -> None:
        self.__passwordhash = passwordHash

    def setRole(self, role) -> None:
        self.__role = role

    def setAddress(self, address: Address) -> None:
        self.__address = address

    def setAddress(self, street, houseNumber, city, postCode, country) -> None:
        address = Address()
        address.setStreet(street)
        address.setHouseNumber(houseNumber)
        address.setCity(city)
        address.setPostCode(postCode)
        address.setCountry(country)
        self.__address = address

    def setFirstName(self, firstName) -> None:
        self.__firstname = firstName

    def setLastName(self, lastName) -> None:
        self.__lastname = lastName

    def setBirthday(self, year: int, month: int, day: int) -> None:
        self.__birthday = f"{year}-{month}-{day}"

    def setBirthday(self, birthday: str) -> None:
        self.__birthday = birthday

    # Override get_id() to return the ID as a string
    def get_id(self) -> str:
        return str(self.__id) if self.__id is not None else None

    # Other methods
    def getDataObject(self) -> dict:
        dataObject = {
            "id": self.getId(),
            "email": self.getEmail(),
            "passwordhash": self.getPasswordHash(),
            "role": self.getRole(),
            "address": self.__address,
            "firstname": self.__firstname,
            "lastname": self.__lastname,
            "birthday": self.__birthday
        }
        return dataObject