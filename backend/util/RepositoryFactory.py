from ..db.Database import Database
from ..users.UserRepository import UserRepository
from ..campsite.CampsiteRepository import CampsiteRepository
from ..campsite.module_campsite.CampsiteModuleRepository import CampsiteModuleRepository
from ..modules.ModuleRepository import ModuleRepository
from ..address.AddressRepository import AddressRepository
from ..users.CampsiteAdminRepository import CampsiteAdminRepository
from ..transaction.TransactionRepository import TransactionRepository

class RepositoryFactory:
    def __init__(self, db: Database):
        self.__db = db
        self.__user_repository = None
        self.__campsite_repository = None
        self.__campsite_module_repository = None
        self.__module_repository = None
        self.__address_repository = None
        self.__campsite_admin_repository = None
        self.__transaction_repository = None

    def getUserRepository(self) -> UserRepository:
        if self.__user_repository is None:
            self.__user_repository = UserRepository(self.__db)
        return self.__user_repository

    def getCampsiteRepository(self) -> CampsiteRepository:
        if self.__campsite_repository is None:
            self.__campsite_repository = CampsiteRepository()
        return self.__campsite_repository

    def getCampsiteModuleRepository(self) -> CampsiteModuleRepository:
        if self.__campsite_module_repository is None:
            self.__campsite_module_repository = CampsiteModuleRepository()
        return self.__campsite_module_repository

    def getModuleRepository(self) -> ModuleRepository:
        if self.__module_repository is None:
            self.__module_repository = ModuleRepository(self.__db)
        return self.__module_repository

    def getAddressRepository(self) -> AddressRepository:
        if self.__address_repository is None:
            self.__address_repository = AddressRepository()
        return self.__address_repository

    def getCampsiteAdminRepository(self) -> CampsiteAdminRepository:
        if self.__campsite_admin_repository is None:
            self.__campsite_admin_repository = CampsiteAdminRepository(self.__db, self.getUserRepository())
        return self.__campsite_admin_repository

    def getTransactionRepository(self) -> TransactionRepository:
        if self.__transaction_repository is None:
            self.__transaction_repository = TransactionRepository(self.__db)
        return self.__transaction_repository