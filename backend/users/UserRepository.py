from .UserMapper import *
from .User import *
from ..db.Database import Database
from ..address.AddressRepository import AddressRepository

# holds and provides all user objects
class UserRepository:
    __users = []
    __userMapper = None
    __db = None

    def __init__(self, db: Database):
        self.__db = db

    # Get methods
    def getUsers(self) -> List[User]:
        # if the users aren't loaded yet, they should be loaded.
        if len(self.__users) == 0:
            self.initializeUsers()
        return self.__users

    def getUserMapper(self) -> UserMapper:
        if self.__userMapper is None:
            self.__userMapper = UserMapper()
        return self.__userMapper

    def getUserById(self, id) -> User | None:
        # Convert id to int if not string
        try:
            id = int(id)
        except (ValueError, TypeError):
            print(f"Invalid ID format: {id}")
            return None

        # Check list
        if len(self.__users) == 0:
            self.initializeUsers()
        for userObject in self.__users:
            try:
                if int(userObject.getId()) == id:
                    print(f"Found user in cache: {userObject.getUsername()} (ID: {id})")
                    return userObject
            except (ValueError, TypeError):
                continue

        # Fallback: Direkte Datenbankabfrage
        print(f"User with ID {id} not found in cache, querying database")
        result = self.__db.execute(
            f"SELECT users.id, users.username, users.email, users.passwordhash, users.role, users.firstname, users.lastname, users.birthday, "
            f"address.streetName, address.houseNumber, city.name AS cityName, city.postCode, country.name AS countryName, users.fk_campsiteAdmin "
            f"FROM users "
            f"LEFT JOIN address ON users.fk_address = address.id "
            f"LEFT JOIN city ON address.fk_city = city.id "
            f"LEFT JOIN country ON city.fk_country = country.id "
            f"WHERE users.id = %s", (id,)
        )

        if result:
            userTuple = result[0]
            userObject = User()
            userObject.setId(userTuple[0])
            userObject.setUsername(userTuple[1])
            userObject.setEmail(userTuple[2])
            userObject.setPasswordHash(userTuple[3])
            userObject.setRole(userTuple[4])
            userObject.setFirstName(userTuple[5])
            userObject.setLastName(userTuple[6])
            userObject.setBirthday(userTuple[7])
            userObject.setAddress(userTuple[8] or "", userTuple[9] or "", userTuple[10] or "", userTuple[11] or "", userTuple[12] or "")
            userObject.setCampsiteAdminId(userTuple[13])
            print(f"Loaded user from database: {userObject.getUsername()} (ID: {id})")
            self.__users.append(userObject)  # Update cache
            return userObject

        print(f"No user found for ID: {id}")
        return None

    def getUserByUsername(self, username) -> User | None:
        if len(self.__users) == 0:
            self.initializeUsers()
        for userObject in self.__users:
            if userObject.getUsername() == username:
                return userObject
        # Fallback: Direct database access
        result = self.__db.execute(
            f"SELECT users.id, users.username, users.email, users.passwordhash, users.role, users.firstname, users.lastname, users.birthday, "
            f"address.streetName, address.houseNumber, city.name AS cityName, city.postCode, country.name AS countryName, users.fk_campsiteAdmin "
            f"FROM users "
            f"LEFT JOIN address ON users.fk_address = address.id "
            f"LEFT JOIN city ON address.fk_city = city.id "
            f"LEFT JOIN country ON city.fk_country = country.id "
            f"WHERE users.username = %s", (username,)
        )
        if result:
            userTuple = result[0]
            userObject = User()
            userObject.setId(userTuple[0])
            userObject.setUsername(userTuple[1])
            userObject.setEmail(userTuple[2])
            userObject.setPasswordHash(userTuple[3])
            userObject.setRole(userTuple[4])
            userObject.setFirstName(userTuple[5])
            userObject.setLastName(userTuple[6])
            userObject.setBirthday(userTuple[7])
            userObject.setAddress(userTuple[8] or "", userTuple[9] or "", userTuple[10] or "", userTuple[11] or "", userTuple[12] or "")
            userObject.setCampsiteAdminId(userTuple[13])
            self.__users.append(userObject)  # Cache aktualisieren
            return userObject
        return None

    def getUserByEmail(self, email) -> User | None:
        if len(self.__users) == 0:
            self.initializeUsers()
        for userObject in self.__users:
            if userObject.getEmail() == email:
                return userObject
        # Fallback: Direct database access
        result = self.__db.execute(
            f"SELECT users.id, users.username, users.email, users.passwordhash, users.role, users.firstname, users.lastname, users.birthday, "
            f"address.streetName, address.houseNumber, city.name AS cityName, city.postCode, country.name AS countryName, users.fk_campsiteAdmin "
            f"FROM users "
            f"LEFT JOIN address ON users.fk_address = address.id "
            f"LEFT JOIN city ON address.fk_city = city.id "
            f"LEFT JOIN country ON city.fk_country = country.id "
            f"WHERE users.email = %s", (email,)
        )
        if result:
            userTuple = result[0]
            userObject = User()
            userObject.setId(userTuple[0])
            userObject.setUsername(userTuple[1])
            userObject.setEmail(userTuple[2])
            userObject.setPasswordHash(userTuple[3])
            userObject.setRole(userTuple[4])
            userObject.setFirstName(userTuple[5])
            userObject.setLastName(userTuple[6])
            userObject.setBirthday(userTuple[7])
            userObject.setAddress(userTuple[8] or "", userTuple[9] or "", userTuple[10] or "", userTuple[11] or "", userTuple[12] or "")
            userObject.setCampsiteAdminId(userTuple[13])
            self.__users.append(userObject)  # Cache aktualisieren
            return userObject
        return None

    def getDb(self) -> Database:
        return self.__db

    # saves user object and returns the id of the user
    def saveUserObject(self, addressRepository: AddressRepository, userObject: User) -> int:
        return self.__userMapper.saveUser(userObject, addressRepository, self.__db)

    # Set methods
    def setUsers(self, users: List[User]) -> None:
        self.__users = users

    def setUserMapper(self, userMapper: UserMapper) -> None:
        self.__userMapper = userMapper

    def initializeUsers(self):
        self.setUsers(self.getUserMapper().getUserObjects(self.__db))

    def setDb(self, db: Database):
        self.__db = db

    # Other methods
    def updateUserObject(self, addressRepository: AddressRepository, userObject: User) -> None:
        self.getUserMapper().updateUser(userObject, addressRepository, self.__db)
        # update user list
        self.initializeUsers()