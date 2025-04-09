from .UserMapper import *
from .User import *
from ..db.Database import Database
from ..address.AddressRepository import AddressRepository

# holds and provides all user objects
class UserRepository:
    __users      = []
    __userMapper = None
    __db         = None

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

    def getUserById(self, id) -> User|None:
        if len(self.__users) == 0:
            self.initializeUsers()
        for userObject in self.__users:
            if userObject.getId() == id:
                return userObject

    def getUserByUsername(self, username) -> User|None:
        if len(self.__users) == 0:
            self.initializeUsers()
        for userObject in self.__users:
            if userObject.getUsername() == username:
                return userObject

    def getUserByEmail(self, email) -> User|None:
        if len(self.__users) == 0:
            self.initializeUsers()
        for userObject in self.__users:
            if userObject.getEmail() == email:
                return userObject

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