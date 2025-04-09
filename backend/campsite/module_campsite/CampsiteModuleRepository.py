from .CampsiteModuleMapper import CampsiteModuleMapper
from .CampsiteModule import CampsiteModule
from typing import List
from ...db.Database import Database
from ...modules.ModuleRepository import ModuleRepository
from ...modules.Module import Module

# holds and provides all campsite-module-connection objects
class CampsiteModuleRepository:
    __campsiteModules      = []
    __campsiteModuleMapper = None

# Get methods
    def getCampsiteModules(self, db: Database) -> List[CampsiteModule]:
        # If the campsite-modules aren't loaded yet, they should be loaded
        if len(self.__campsiteModules) == 0:
            self.setCampsiteModules(self.getCampsiteModuleMapper().getCampsiteModules(db))
        return self.__campsiteModules

    def getCampsiteModuleMapper(self) -> CampsiteModuleMapper:
        if self.__campsiteModuleMapper is None:
            self.__campsiteModuleMapper = CampsiteModuleMapper()
        return self.__campsiteModuleMapper

    def getCampsiteModulesForCampsiteId(self, campsiteId: int, db: Database, moduleRepository: ModuleRepository) -> List[Module]:
        # If the campsite-modules aren't loaded yet, they should be loaded
        if len(self.__campsiteModules) == 0:
            self.setCampsiteModules(self.getCampsiteModuleMapper().getCampsiteModules(db))

        modulesForCampsite = []

        for campsiteModule in self.__campsiteModules:
            if campsiteModule.getFkCampsiteId() == campsiteId:
                modulesForCampsite.append(moduleRepository.getModuleForModuleId(campsiteModule.getFkModuleId(), db))
        return modulesForCampsite

# Set methods
    def setCampsiteModules(self, campsiteModules: List[CampsiteModule]) -> None:
        self.__campsiteModules = campsiteModules

    def setCampsiteModuleMapper(self, campsiteModuleMapper: CampsiteModuleMapper) -> None:
        self.__campsiteModuleMapper = campsiteModuleMapper