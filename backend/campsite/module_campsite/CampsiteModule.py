# Data class for campsite module connection objects
class CampsiteModule:
    __id            = None
    __fk_campsiteId = None
    __fk_moduleId   = None

# Get methods
    def getId(self) -> int:
        return self.__id

    def getFkCampsiteId(self) -> int:
        return self.__fk_campsiteId

    def getFkModuleId(self) -> int:
        return self.__fk_moduleId

# Set methods
    def setId(self, id: int) -> None:
        self.__id = id

    def setFkCampsiteId(self, fkCampsiteId: int) -> None:
        self.__fk_campsiteId = fkCampsiteId

    def setFkModuleId(self, fkModuleId: int) -> None:
        self.__fk_moduleId = fkModuleId

# Other methods
    # transforms this object in a data object only containing the relevant data
    def getDataObject(self) -> dict:
        dataObject = {
            "id": self.getId(),
            "fk_campsiteId": self.getFkCampsiteId(),
            "fk_moduleId": self.getFkModuleId()
        }

        return dataObject