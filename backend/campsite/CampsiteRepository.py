from .CampsiteMapper import CampsiteMapper
from typing import List
from .Campsite import Campsite
from ..db.Database import Database
from .module_campsite.CampsiteModuleRepository import CampsiteModuleRepository
from ..modules.ModuleRepository import ModuleRepository
from ..address.AddressRepository import AddressRepository


# holds and provides all campsite objects
class CampsiteRepository:
    __campsites      = []
    __campsiteMapper = None

# Get methods
    def getCampsites(self, db: Database, campsiteModuleRepository: CampsiteModuleRepository, moduleRepository: ModuleRepository) -> List[Campsite]:
        # if the campsites aren't loaded yet, they should be loaded.
        if len(self.__campsites) == 0:
            self.setCampsites(self.getCampsiteMapper().getCampsiteObjects(db, campsiteModuleRepository, moduleRepository))
        return self.__campsites

    def getCampsiteMapper(self) -> CampsiteMapper:
        if self.__campsiteMapper is None:
            self.__campsiteMapper = CampsiteMapper()
        return self.__campsiteMapper

    # returns all campsite objects as transferred data objects
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
                    campsite.setAddress("", "", "", "", "")  # Fallback-Address
                return campsite
        return None

# Set methods
    def setCampsites(self, campsites: List[Campsite]) -> None:
        self.__campsites = campsites

    def setCampsiteMapper(self, campSiteMapper: CampsiteMapper) -> None:
        self.__campsiteMapper = campSiteMapper

# Other methods
    def updateCampsiteObject(self, addressRepository: AddressRepository, campsiteObject: Campsite, db: Database) -> None:
        addressId = addressRepository.saveAddressObject(campsiteObject.getAddress(), db)
        db.execute(
            "UPDATE campsite SET "
            "name = %s, "
            "description = %s, "
            "fk_address = %s "
            "WHERE id = %s",
            (campsiteObject.getName(), campsiteObject.getDescription(), addressId, campsiteObject.getId()),
            commit=True
        )

    # Updates the modules of specific campsite in the cache
    def updateCampsiteModules(self, campsite_id: int, db: Database, campsite_module_repository: CampsiteModuleRepository) -> None:
        for campsite in self.__campsites:
            if str(campsite.getId()) == str(campsite_id):
                # Reload modules
                campsite.setModules(campsite_module_repository.getModulesByCampsiteId(campsite_id, db))
                break