from typing import List
from .Module import Module
from backend.db.Database import *

# loads the modules from the database and
# creates module objects from them
class ModuleMapper:

    __moduleObjects = []

    def getModuleObjects(self, db: Database, rebuildObjects: bool = False):
        # Check if list is already initialized. If yes, skip refilling for performance reasons
        if len(self.__moduleObjects) == 0 or rebuildObjects == True:
            self.__moduleObjects= []

        selectedModules = db.execute(
            f"SELECT modules.id, modules.moduleName FROM modules"
        )

        # create module objects
        for moduleTuple in selectedModules:
            moduleObject = Module()

            moduleObject.setId(moduleTuple[0])
            moduleObject.setName(moduleTuple[1])

            self.__moduleObjects.append(moduleObject)

        return self.__moduleObjects