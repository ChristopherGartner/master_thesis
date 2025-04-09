from backend.db.Database import *
from .CampsiteModule import *
from typing import List

# loads the Campsite-Module connections from the m:n conection table and
# creates Campsite-Module objects from them
class CampsiteModuleMapper:

    __campsiteModules = []

    # Loads the campsite-module connection data from the database and creates campsite-module
    # objects out of it.
    #
    # @param db = Database object
    # @param rebuildObjects = Boolean whether the campsite objects should be rebuilt
    def getCampsiteModules(self, db: Database, rebuildObjects: bool = False) -> List[CampsiteModule]:
        # Check if list is already initialized. If yes, skip refilling for performance reasons
        if len(self.__campsiteModules) == 0 or rebuildObjects == True:
            self.__campsiteModules = []

            selectedCampsiteModules = db.execute(
                f"SELECT campsiteModules.id, campsiteModules.fk_campsiteId, campsiteModules.fk_modulesId FROM campsiteModules"
            )

            # Create campsite objects
            for campsiteModuleTuple in selectedCampsiteModules:
                campsiteModuleObject = CampsiteModule()
                campsiteModuleObject.setId(campsiteModuleTuple[0])
                campsiteModuleObject.setFkCampsiteId(campsiteModuleTuple[1])
                campsiteModuleObject.setFkModuleId(campsiteModuleTuple[2])

                self.__campsiteModules.append(campsiteModuleObject)

        return self.__campsiteModules