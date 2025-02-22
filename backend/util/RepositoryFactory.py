from ..campsite.CampsiteRepository import CampsiteRepository

# used for managing all repositories of the application
class RepositoryFactory:
    __campsiteRepository = None

    # All repositories need to be initialized here
    def __init__(self):
        self.__campsiteRepository = CampsiteRepository()

# Get methods
    def getCampsiteRepository(self):
        return self.__campsiteRepository

# Set methods
    def setCampsiteRepository(self, campsiteRepository: CampsiteRepository):
        self.__campsiteRepository = campsiteRepository
