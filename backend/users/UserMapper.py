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
                f"address.streetName, address.houseNumber, city.name AS cityName, city.postCode, country.name AS countryName, users.fk_campsiteAdmin "
                f"FROM users "
                f"LEFT JOIN address ON users.fk_address = address.id "
                f"LEFT JOIN city ON address.fk_city = city.id "
                f"LEFT JOIN country ON city.fk_country = country.id"
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
                addressStreetName  = userTuple[8] or ""
                addressHouseNumber = userTuple[9] or ""
                addressCityName    = userTuple[10] or ""
                addressPostCode    = userTuple[11] or ""
                addressCountryName = userTuple[12] or ""
                fk_campsiteAdmin   = userTuple[13]

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
                userObject.setCampsiteAdminId(fk_campsiteAdmin)

                self.__userObjects.append(userObject)

        return self.__userObjects

    def __saveUser(self, username: str, email: str, passwordHash: str, role: str, fk_address: int, firstName: str, lastName: str, birthday: str, fk_campsiteAdmin: int | None, db: Database) -> None:
        db.execute(
            "INSERT INTO users (username, email, passwordhash, role, fk_address, firstname, lastname, birthday, fk_campsiteAdmin) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (username, email, passwordHash, role, fk_address, firstName, lastName, birthday, fk_campsiteAdmin),
            commit=True
        )

    def __getUserId(self, username: str, email: str, passwordHash: str, role: str, fk_address: int, firstName: str, lastName: str, birthday: str, fk_campsiteAdmin: int | None, db: Database) -> int|None:
        result = db.execute(
            "SELECT users.id "
            "FROM users "
            "WHERE users.username = %s AND users.email = %s "
            "AND users.passwordhash = %s AND users.role = %s AND users.fk_address = %s "
            "AND users.firstname = %s AND users.lastname = %s AND users.birthday = %s "
            "AND (users.fk_campsiteAdmin = %s OR (users.fk_campsiteAdmin IS NULL AND %s IS NULL))",
            (username, email, passwordHash, role, fk_address, firstName, lastName, birthday, fk_campsiteAdmin, fk_campsiteAdmin)
        )

        # Check, whether result exists and extract id
        if result and len(result) > 0:
            return result[0][0]
        return None

    def saveUser(self, userObject: User, addressRepository: AddressRepository, db: Database) -> int:
        addressId = addressRepository.saveAddressObject(userObject.getAddress(), db)
        self.__saveUser(
            userObject.getUsername(),
            userObject.getEmail(),
            userObject.getPasswordHash(),
            userObject.getRole(),
            addressId,
            userObject.getFirstName(),
            userObject.getLastName(),
            userObject.getBirthday(),
            userObject.getCampsiteAdminId(),
            db
        )
        userId = self.__getUserId(
            userObject.getUsername(),
            userObject.getEmail(),
            userObject.getPasswordHash(),
            userObject.getRole(),
            addressId,
            userObject.getFirstName(),
            userObject.getLastName(),
            userObject.getBirthday(),
            userObject.getCampsiteAdminId(),
            db
        )
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
            "fk_address = %s, "
            "fk_campsiteAdmin = %s "
            "WHERE id = %s",
            (
                userObject.getUsername(),
                userObject.getEmail(),
                userObject.getPasswordHash(),
                userObject.getFirstName(),
                userObject.getLastName(),
                userObject.getBirthday(),
                addressId,
                userObject.getCampsiteAdminId(),
                userObject.getId()
            ),
            commit=True
        )
        # Cache update
        self.getUserObjects(db, rebuildObjects=True)