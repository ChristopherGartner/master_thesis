# Data class for campsites*
class Campsite:
    __id      = None
    __name    = None
    __address = None

# Get methods
    def getId(self):
        return self.__id

    def getName(self):
        return self.__name

    def getAddress(self):
        return self.__address

# Set methods
    def setId(self, id: str):
        self.__id = id

    def setName(self, name: str):
        self.__name = name

    def setAddress(self, address: str):
        self.__address = address

# Other methods
    # transforms this object in a data object only containing the relevant data
    def getDataObject(self):
        dataObject = {
            "id": self.getId(),
            "name": self.getName(),
            "address": self.getAddress()
        }

        return dataObject