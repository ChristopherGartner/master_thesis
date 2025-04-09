from .ModuleMapper import ModuleMapper
from .Module import Module
from typing import List
from ..db.Database import Database

# holds and provides all address objects
class ModuleRepository:
    __modules      = []
    __moduleMapper = None

# Get methods
    def getModules(self, db: Database) -> List[Module]:
        # If the modules aren't loaded yet, they should be loaded
        if len(self.__modules) == 0:
            self.setModules(self.getModuleMapper().getModuleObjects(db))
        return self.__modules

    def getModuleMapper(self) -> ModuleMapper:
        if self.__moduleMapper is None:
            self.__moduleMapper = ModuleMapper()
        return self.__moduleMapper

    def getModuleForModuleId(self, moduleId: int, db: Database) -> Module|None:
        # If the modules aren't loaded yet, they should be loaded
        if len(self.__modules) == 0:
            self.setModules(self.getModuleMapper().getModuleObjects(db))

        for module in self.__modules:
            if module.getId() == moduleId:
                return module

# Set methods
    def setModules(self, modules: List[Module]) -> None:
        self.__modules = modules

    def setModuleMapper(self, moduleMapper: ModuleMapper) -> None:
        self.__moduleMapper = moduleMapper