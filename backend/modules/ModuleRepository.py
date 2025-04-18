from .ModuleMapper import ModuleMapper
from .Module import Module
from typing import List
from ..db.Database import Database

class ModuleRepository:
    __modules = []
    __moduleMapper = None
    __db = None

    def __init__(self, db: Database):
        self.__db = db

    # Get methods
    def getModules(self, db: Database = None) -> List[Module]:
        # Verwende die im Konstruktor übergebene db, falls keine db übergeben wurde
        db = db or self.__db
        if len(self.__modules) == 0:
            self.setModules(self.getModuleMapper().getModuleObjects(db))
        return self.__modules

    def getModuleMapper(self) -> ModuleMapper:
        if self.__moduleMapper is None:
            self.__moduleMapper = ModuleMapper()
        return self.__moduleMapper

    def getModuleForModuleId(self, moduleId: int, db: Database = None) -> Module | None:
        db = db or self.__db
        if len(self.__modules) == 0:
            self.setModules(self.getModuleMapper().getModuleObjects(db))
        for module in self.__modules:
            if module.getId() == moduleId:
                return module
        return None

    # Set methods
    def setModules(self, modules: List[Module]) -> None:
        self.__modules = modules

    def setModuleMapper(self, moduleMapper: ModuleMapper) -> None:
        self.__moduleMapper = moduleMapper