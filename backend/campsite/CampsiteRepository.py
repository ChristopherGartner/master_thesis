from .CampsiteMapper import CampsiteMapper
from typing import List
from .Campsite import Campsite
from ..db.Database import Database
from .module_campsite.CampsiteModuleRepository import CampsiteModuleRepository
from ..modules.ModuleRepository import ModuleRepository
from ..address.AddressRepository import AddressRepository

class CampsiteRepository:
    __campsites      = []
    __campsiteMapper = None

# Get methods
    def getCampsites(self, db: Database, campsiteModuleRepository: CampsiteModuleRepository, moduleRepository: ModuleRepository) -> List[Campsite]:
        if len(self.__campsites) == 0:
            self.setCampsites(self.getCampsiteMapper().getCampsiteObjects(db, campsiteModuleRepository, moduleRepository))
        return self.__campsites

    def getCampsiteMapper(self) -> CampsiteMapper:
        if self.__campsiteMapper is None:
            self.__campsiteMapper = CampsiteMapper()
        return self.__campsiteMapper

    def getCampsitesAsDataObjects(self, db: Database, campsiteModuleRepository: CampsiteModuleRepository, moduleRepository: ModuleRepository) -> List[dict]:
        campsiteDataObjects = []
        for campsite in self.getCampsites(db, campsiteModuleRepository, moduleRepository):
            campsiteDataObjects.append(campsite.getDataObject())
        return campsiteDataObjects

    def getCampsiteById(self, campsite_id: int, db: Database, campsiteModuleRepository: CampsiteModuleRepository,
                        moduleRepository: ModuleRepository) -> Campsite | None:
        campsites = self.getCampsites(db, campsiteModuleRepository, moduleRepository)
        for campsite in campsites:
            if str(campsite.getId()) == str(campsite_id):
                if campsite.getAddress() is None:
                    campsite.setAddress("", "", "", "", "")
                return campsite
        return None

# Set methods
    def setCampsites(self, campsites: List[Campsite]) -> None:
        self.__campsites = campsites

    def setCampsiteMapper(self, campSiteMapper: CampsiteMapper) -> None:
        self.__campsiteMapper = campSiteMapper

# Other methods
    def clearCache(self) -> None:
        self.__campsites = []

    def updateCampsiteObject(self, addressRepository: AddressRepository, campsiteObject: Campsite, db: Database, logo_path: str = None) -> None:
        addressId = addressRepository.saveAddressObject(campsiteObject.getAddress(), db)
        params = (campsiteObject.getName(), campsiteObject.getDescription(), addressId, logo_path, campsiteObject.getId())
        db.execute(
            "UPDATE campsite SET "
            "name = %s, "
            "description = %s, "
            "fk_address = %s, "
            "logo_path = %s "
            "WHERE id = %s",
            params,
            commit=True
        )

    def updateCampsiteModules(self, campsite_id: int, db: Database, campsite_module_repository: CampsiteModuleRepository) -> None:
        for campsite in self.__campsites:
            if str(campsite.getId()) == str(campsite_id):
                campsite.setModules(campsite_module_repository.getModulesByCampsiteId(campsite_id, db))
                break