# Data class for address objects
class Address:
    __id          = None
    __street      = None
    __houseNumber = None
    __city        = None
    __postCode    = None
    __country     = None

# Get methods
    def getId(self) -> str:
        return self.__id

    def getStreet(self) -> str:
        return self.__street

    def getHouseNumber(self) -> str:
        return self.__houseNumber

    def getCity(self) -> str:
        return self.__city

    def getPostCode(self) -> str:
        return self.__postCode

    def getCountry(self) -> str:
        return self.__country

# Set methods
    def setId(self, id):
        self.__id = id

    def setStreet(self, street) -> None:
        self.__street = street

    def setHouseNumber(self, houseNumber) -> None:
        self.__houseNumber = houseNumber

    def setCity(self, city) -> None:
        self.__city = city

    def setPostCode(self, postCode) -> None:
        self.__postCode = postCode

    def setCountry(self, country) -> None:
        self.__country = country

# Other methods
    # transforms this object in a data object only containing the relevant data
    def getDataObject(self) -> dict:
        dataObject = {
            "id": self.getId(),
            "street": self.getStreet(),
            "houseNumber": self.getHouseNumber(),
            "city": self.getCity(),
            "postCode": self.getPostCode(),
            "country": self.getCountry()
        }

        return dataObject
