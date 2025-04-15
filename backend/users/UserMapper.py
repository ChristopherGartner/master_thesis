from .User import *
from typing import List
from backend.db.Database import *
from ..address.AddressRepository import AddressRepository

# loads the users from the database and
# creates User objects from them
class UserMapper:

    __userObjects = []

    def getUserObjects(self, db: Database, rebuildObjects: bool = False) -> List[User]:
        # Check if list is already initialized. If yes, skip refilling for performance reasons
        if len(self.__userObjects) == 0 or rebuildObjects == True:
            self.__userObjects = []

            selectedUsers = db.execute(
                f"SELECT users.id, users.username, users.email, users.passwordhash, users.role, users.firstname, users.lastname, users.birthday, "
                f"address.streetName, address.houseNumber, city.name AS cityName, city.postCode, country.name AS countryName "
                f"FROM users "
                f"INNER JOIN address ON users.fk_address = address.id "
                f"INNER JOIN city ON address.fk_city = city.id "
                f"INNER JOIN country ON city.fk_country = country.id"
            )

            # Create user objects
            for userTuple in selectedUsers:
                userId           = userTuple[0]
                userUsername     = userTuple[1]
                userEmail        = userTuple[2]
                userPasswordHash = userTuple[3]
                userRole         = userTuple[4]
                userFirstName    = userTuple[5]
                userLastName     = userTuple[6]
                userBirthday     = userTuple[7]

                addressStreetName  = userTuple[8]
                addressHouseNumber = userTuple[9]
                addressCityName    = userTuple[10]
                addressPostCode    = userTuple[11]
                addressCountryName = userTuple[12]

                userObject = User()
                userObject.setId(userId)
                userObject.setUsername(userUsername)
                userObject.setEmail(userEmail)
                userObject.setPasswordHash(userPasswordHash)
                userObject.setRole(userRole)
                userObject.setFirstName(userFirstName)
                userObject.setLastName(userLastName)
                userObject.setBirthday(userBirthday)
                userObject.setAddress(addressStreetName, addressHouseNumber, addressCityName, addressPostCode, addressCountryName)

                self.__userObjects.append(userObject)

        return self.__userObjects

    def __saveUser(self, username: str, email: str, passwordHash: str, role: str, fk_address: int, firstName: str, lastName: str, birthday: str, db: Database) -> None:
        db.execute(
            "INSERT INTO users (username, email, passwordhash, role, fk_address, firstname, lastname, birthday) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (username, email, passwordHash, role, fk_address, firstName, lastName, birthday),
            commit=True
        )

    def __getUserId(self, username: str, email: str, passwordHash: str, role: str, fk_address: int, firstName: str, lastName: str, birthday: str, db: Database) -> int|None:
        result = db.execute(
            "SELECT users.id "
            "FROM users "
            "WHERE users.username = %s AND users.email = %s "
            "AND users.passwordhash = %s AND users.role = %s AND users.fk_address = %s "
            "AND users.firstname = %s AND users.lastname = %s AND users.birthday = %s",
            (username, email, passwordHash, role, fk_address, firstName, lastName, birthday)
        )

        # Check, whether result exists and extract id
        if result and len(result) > 0:
            return result[0][0]
        return None

    def saveUser(self, userObject: User, addressRepository: AddressRepository, db: Database) -> int:
        addressId = addressRepository.saveAddressObject(userObject.getAddress(), db)
        self.__saveUser(userObject.getUsername(), userObject.getEmail(), userObject.getPasswordHash(), userObject.getRole(), addressId, userObject.getFirstName(), userObject.getLastName(), userObject.getBirthday(), db)
        userId = self.__getUserId(userObject.getUsername(), userObject.getEmail(), userObject.getPasswordHash(), userObject.getRole(), addressId, userObject.getFirstName(), userObject.getLastName(), userObject.getBirthday(), db)
        # Cache aktualisieren
        self.getUserObjects(db, rebuildObjects=True)
        return userId

    def updateUser(self, userObject: User, addressRepository: AddressRepository, db: Database) -> None:
        # update address
        addressId = addressRepository.saveAddressObject(userObject.getAddress(), db)

        # update user data
        db.execute(
            "UPDATE users SET "
            "username = %s, "
            "email = %s, "
            "passwordhash = %s, "
            "firstname = %s, "
            "lastname = %s, "
            "birthday = %s, "
            "fk_address = %s "
            "WHERE id = %s",
            (userObject.getUsername(), userObject.getEmail(), userObject.getPasswordHash(), userObject.getFirstName(), userObject.getLastName(), userObject.getBirthday(), addressId, userObject.getId()),
            commit=True
        )
        # Cache update
        self.getUserObjects(db, rebuildObjects=True)