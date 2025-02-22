# Data class for campsites*
class Campsite:
    __id      = None
    __name    = None
    __address = None

# Get methods
    def getId(self) -> str:
        return self.__id

    def getName(self) -> str:
        return self.__name

    def getAddress(self) -> str:
        return self.__address

# Set methods
    def setId(self, id: str) -> None:
        self.__id = id

    def setName(self, name: str) -> None:
        self.__name = name

    def setAddress(self, address: str) -> None:
        self.__address = address

# Other methods
    # transforms this object in a data object only containing the relevant data
    def getDataObject(self) -> dict:
        dataObject = {
            "id": self.getId(),
            "name": self.getName(),
            "address": self.getAddress()
        }

        return dataObject