from .CampsiteModuleMapper import CampsiteModuleMapper
from .CampsiteModule import CampsiteModule
from typing import List
from ...db.Database import Database
from ...modules.ModuleRepository import ModuleRepository
from ...modules.Module import Module

class CampsiteModuleRepository:
    __campsiteModules      = []
    __campsiteModuleMapper = None

    def getCampsiteModules(self, db: Database) -> List[CampsiteModule]:
        if len(self.__campsiteModules) == 0:
            self.setCampsiteModules(self.getCampsiteModuleMapper().getCampsiteModules(db))
        return self.__campsiteModules

    def getCampsiteModuleMapper(self) -> CampsiteModuleMapper:
        if self.__campsiteModuleMapper is None:
            self.__campsiteModuleMapper = CampsiteModuleMapper()
        return self.__campsiteModuleMapper

    def getCampsiteModulesForCampsiteId(self, campsiteId: int, db: Database, moduleRepository: ModuleRepository, rebuildCampsiteModules = False) -> List[Module]:
        if len(self.__campsiteModules) == 0 or rebuildCampsiteModules:
            self.setCampsiteModules(self.getCampsiteModuleMapper().getCampsiteModules(db))

        modulesForCampsite = []

        for campsiteModule in self.__campsiteModules:
            if campsiteModule.getFkCampsiteId() == campsiteId:
                modulesForCampsite.append(moduleRepository.getModuleForModuleId(campsiteModule.getFkModuleId(), db))
        return modulesForCampsite

    def getModulesByCampsiteId(self, campsiteId: int, db: Database) -> List[Module]:
        return self.getCampsiteModulesForCampsiteId(campsiteId, db, ModuleRepository(db), True)

    def setCampsiteModules(self, campsiteModules: List[CampsiteModule]) -> None:
        self.__campsiteModules = campsiteModules

    def setCampsiteModuleMapper(self, campsiteModuleMapper: CampsiteModuleMapper) -> None:
        self.__campsiteModuleMapper = campsiteModuleMapper

    def updateCampsiteModules(self, campsite_id: int, module_ids: List[str], db: Database, campsiteRepository) -> None:
        db.execute(
            "DELETE FROM campsiteModules WHERE fk_campsiteId = %s",
            (campsite_id,),
            commit=True
        )
        for module_id in module_ids:
            if module_id:
                db.execute(
                    "INSERT INTO campsiteModules (fk_campsiteId, fk_modulesId) VALUES (%s, %s)",
                    (campsite_id, int(module_id)),
                    commit=True
                )
        self.setCampsiteModules(self.getCampsiteModuleMapper().getCampsiteModules(db, rebuildObjects=True))
        # Update modules of campsite
        campsiteRepository.updateCampsiteModules(campsite_id, db, self)

    def clearCache(self) -> None:
        self.__campsiteModules = []