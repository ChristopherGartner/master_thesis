from .CampsiteMapper import CampsiteMapper
from typing import List
from .Campsite import Campsite
from ..db.Database import Database
from .module_campsite.CampsiteModuleRepository import CampsiteModuleRepository
from ..modules.ModuleRepository import ModuleRepository
from ..address.AddressRepository import AddressRepository

class CampsiteRepository:
    __campsites = []
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

    def getAvailableFeatures(self) -> List[dict]:
        # Define available features with type, SVG icon, and translation key
        return [
            {'id': 'wlan', 'type': 'checkbox', 'icon': 'pictogram_feature_wlan.svg', 'label_key': 'feature_wlan'},
            {'id': 'paw', 'type': 'checkbox', 'icon': 'pictogram_feature_paw.svg', 'label_key': 'feature_paw'},
            {'id': 'shower', 'type': 'text', 'icon': 'pictogram_feature_shower.svg', 'label_key': 'feature_shower'},
            {'id': 'playground', 'type': 'checkbox', 'icon': 'pictogram_feature_playground.svg', 'label_key': 'feature_playground'},
            {'id': 'electric_current', 'type': 'checkbox', 'icon': 'pictogram_feature_electricCurrent.svg', 'label_key': 'feature_electric_current'},
            {'id': 'parking', 'type': 'checkbox', 'icon': 'pictogram_feature_parking.svg', 'label_key': 'feature_parking'},
            {'id': 'swimming', 'type': 'checkbox', 'icon': 'pictogram_feature_swimming.svg', 'label_key': 'feature_swimming'},
            {'id': 'fishing', 'type': 'checkbox', 'icon': 'pictogram_feature_fishing.svg', 'label_key': 'feature_fishing'},
        ]

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

        params = (
            campsiteObject.getName(),
            campsiteObject.getDescription(),
            addressId,
            logo_path,
            campsiteObject.getFeature_wlan(),
            campsiteObject.getFeature_paw(),
            campsiteObject.getFeature_shower(),
            campsiteObject.getFeature_playground(),
            campsiteObject.getFeature_electricCurrent(),
            campsiteObject.getFeature_parking(),
            campsiteObject.getFeature_swimming(),
            campsiteObject.getFeature_fishing(),
            campsiteObject.getId()
        )
        db.execute(
            "UPDATE campsite SET "
                "name = %s, "
                "description = %s, "
                "fk_address = %s, "
                "logo_path = %s, "
                "feature_wlan = %s,"
                "feature_paw = %s, "
                "feature_shower = %s, "
                "feature_playground = %s, "
                "feature_electric_current = %s, "
                "feature_parking = %s, "
                "feature_swimming = %s, "
                "feature_fishing = %s "
            "WHERE campsite.id = %s",
            params,
            commit=True
        )

    def updateCampsiteModules(self, campsite_id: int, db: Database, campsite_module_repository: CampsiteModuleRepository) -> None:
        for campsite in self.__campsites:
            if str(campsite.getId()) == str(campsite_id):
                campsite.setModules(campsite_module_repository.getModulesByCampsiteId(campsite_id, db))
                break