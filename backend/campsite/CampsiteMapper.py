from backend.db.Database import *
from .module_campsite.CampsiteModuleRepository import CampsiteModuleRepository
from ..modules.ModuleRepository import ModuleRepository
from .Campsite import *
import logging

logger = logging.getLogger(__name__)

class CampsiteMapper:
    __campSiteObjects = []

    def clearCache(self) -> None:
        self.__campSiteObjects = []

    def getCampsiteObjects(self, db: Database, campsiteModuleRepository: CampsiteModuleRepository, moduleRepository: ModuleRepository, rebuildObjects: bool = False) -> List[Campsite]:
        from flask_login import current_user
        if len(self.__campSiteObjects) == 0 or rebuildObjects:
            self.__campSiteObjects = []

            query = (
                f"SELECT campsite.id, campsite.name, campsite.description, campsite.isActive, "
                f"campsite.feature_wlan, campsite.feature_swimming, campsite.feature_shower, campsite.feature_playground, campsite.feature_paw, campsite.feature_parking, campsite.feature_electric_current, campsite.feature_fishing, "
                f"address.streetName, address.houseNumber, city.name AS cityName, city.postCode, country.name AS countryName, "
                f"campsite.logo_path "
                f"FROM campsite "
                f"LEFT JOIN address ON campsite.fk_address = address.id "
                f"LEFT JOIN city ON address.fk_city = city.id "
                f"LEFT JOIN country ON city.fk_country = country.id"
            )
            if not (current_user.is_authenticated and current_user.getRole() == "Admin"):
                query += " WHERE campsite.isActive = 1"

            selectedCampsites = db.execute(query)
            logger.debug(f"Query returned {len(selectedCampsites)} campsites")

            for campsiteTuple in selectedCampsites:
                campsiteObject = Campsite()

                # Normal values
                campsiteObject.setId(campsiteTuple[0])
                campsiteObject.setName(campsiteTuple[1])
                campsiteObject.setDescription(campsiteTuple[2])
                campsiteObject.setActive(campsiteTuple[3] == 1)

                # Features
                campsiteObject.setFeature_wlan(campsiteTuple[4] == 1)
                campsiteObject.setFeature_swimming(campsiteTuple[5] == 1)
                campsiteObject.setFeature_shower(campsiteTuple[6] == 1)
                campsiteObject.setFeature_playground(campsiteTuple[7] == 1)
                campsiteObject.setFeature_paw(campsiteTuple[8] == 1)
                campsiteObject.setFeature_parking(campsiteTuple[9] == 1)
                campsiteObject.setFeature_electricCurrent(campsiteTuple[10] == 1)
                campsiteObject.setFeature_fishing(campsiteTuple[11] == 1)

                # Address
                street = campsiteTuple[12] or ""
                house_number = campsiteTuple[13] or ""
                city = campsiteTuple[14] or ""
                post_code = campsiteTuple[15] or ""
                country = campsiteTuple[16] or ""
                logo_path = campsiteTuple[17]  # Fetch logo_path

                campsiteObject.setAddress(street, house_number, city, post_code, country)
                campsiteObject.setLogoPath(logo_path)

                campsiteObject.setModules(campsiteModuleRepository.getCampsiteModulesForCampsiteId(int(campsiteObject.getId()), db, moduleRepository, True))

                self.__campSiteObjects.append(campsiteObject)
                logger.debug(f"Created campsite: {campsiteObject.getName()}")

        return self.__campSiteObjects