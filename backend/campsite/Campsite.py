from ..address.Address import Address

# Data class for campsites*
class Campsite:
    __id          = None
    __name        = None
    __address     = None
    __description = None
    __isActive    = None

# Get methods
    def getId(self) -> str:
        return self.__id

    def getName(self) -> str:
        return self.__name

    def getAddress(self) -> Address:
        return self.__address

    def getDescription(self) -> str:
        return self.__description

    def isActive(self) -> bool:
        return self.isActive()

# Set methods
    def setId(self, id: str) -> None:
        self.__id = id

    def setName(self, name: str) -> None:
        self.__name = name

    def setAddress(self, address: Address) -> None:
        self.__address = address

    def setAddress(self, street, houseNumber, city, postCode, country) -> None:
        address = Address()

        address.setStreet(street)
        address.setHouseNumber(houseNumber)
        address.setCity(city)
        address.setPostCode(postCode)
        address.setCountry(country)

        self.__address = address

    def setDescription(self, description) -> None:
        self.__description = description

    def setActive(self, isActive) -> None:
        self.__isActive = isActive

# Other methods
    # transforms this object in a data object only containing the relevant data
    def getDataObject(self) -> dict:
        dataObject = {
            "id": self.getId(),
            "name": self.getName(),
            "address": self.getAddress(),
            "description": self.getDescription()
        }

        return dataObject