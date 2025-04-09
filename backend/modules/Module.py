# Data class for modules
class Module:
    __id   = None
    __name = None

# Get methods
    def getId(self) -> int:
        return self.__id

    def getName(self) -> str:
        return self.__name

# Set methods
    def setId(self, id: int):
        self.__id = id

    def setName(self, name: str) -> None:
        self.__name = name

# Other methods
    # transforms this object in a data object only containing the relevant data
    def getDataObject(self) -> dict:
        dataObject = {
            "id": self.getId(),
            "name": self.getName()
        }

        return dataObject