from typing import List
from backend.db.Database import *

from .Campsite import *
# loads the campsites from the database and
# creates Campsites objects from them
class CampsiteMapper:

    __campSiteObjects = []

    # Loads the campsite data from the database and creates campsite
    # objects out of it.
    #
    # @param db = Database object
    # @param rebuildObjects = Boolean whether the campsite objects should be rebuilt
    def getCampsiteObjects(self, db: Database, rebuildObjects: bool = False) -> List[Campsite]:
        # Check if list is already initialized. If yes, skip refilling for performance reasons
        if len(self.__campSiteObjects) == 0 or rebuildObjects == True:
            self.__campSiteObjects = []

            selectedCampsites = db.execute(
                f"SELECT campsite.id, campsite.name, campsite.description, campsite.isActive, address.streetName, address.houseNumber, city.name AS cityName, city.postCode, country.name AS countryName "
                f"FROM campsite "
                f"INNER JOIN address ON campsite.fk_address = address.id "
                f"INNER JOIN city ON address.fk_city = city.id "
                f"INNER JOIN country ON city.fk_country = country.id;"
            )

            # Create campsite objects
            for campsiteTuple in selectedCampsites:
                campsiteObject = Campsite()
                campsiteObject.setId(campsiteTuple[0])
                campsiteObject.setName(campsiteTuple[1])
                campsiteObject.setDescription(campsiteTuple[2])

                if campsiteTuple[3] == 1:
                    campsiteObject.setActive(True)
                else:
                    campsiteObject.setActive(False)

                campsiteObject.setAddress(campsiteTuple[4], campsiteTuple[5], campsiteTuple[6], campsiteTuple[7],
                                          campsiteTuple[8])

                self.__campSiteObjects.append(campsiteObject)

        return self.__campSiteObjects



