from ..campsite.CampsiteRepository import CampsiteRepository
from ..users.UserRepository import UserRepository
from ..address.AddressRepository import AddressRepository
from ..db.Database import Database

# used for managing all repositories of the application
class RepositoryFactory:
    __campsiteRepository = None
    __userRepository     = None
    __addressRepository  = None

    # All repositories need to be initialized here
    def __init__(self, db: Database):
        self.__campsiteRepository = CampsiteRepository()
        self.__userRepository     = UserRepository(db)
        self.__addressRepository  = AddressRepository()

# Get methods
    def getCampsiteRepository(self) -> CampsiteRepository:
        return self.__campsiteRepository

    def getUserRepository(self) -> UserRepository:
        return self.__userRepository

    def getAddressRepository(self) -> AddressRepository:
        return self.__addressRepository

# Set methods
    def setCampsiteRepository(self, campsiteRepository: CampsiteRepository) -> None:
        self.__campsiteRepository = campsiteRepository

    def setUserRepository(self, userRepository: UserRepository) -> None:
        self.__userRepository = userRepository

    def setAddressRepository(self, addressRepository: AddressRepository) -> None:
        self.__addressRepository = addressRepository
