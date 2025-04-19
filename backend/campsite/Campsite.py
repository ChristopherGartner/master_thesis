from ..address.Address import Address
from ..modules.Module import Module
from typing import List

class Campsite:
    __id          = None
    __name        = None
    __address     = None
    __description = None
    __isActive    = None
    __modules     = None
    __logo_path   = None  # New attribute for logo path

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
        return self.__isActive

    def getModules(self) -> List[Module]:
        return self.__modules

    def getLogoPath(self) -> str:
        return self.__logo_path or "/static/images/pictogram_campsite_logo_missing.svg"  # Default SVG if none set

# Set methods
    def setId(self, id: str) -> None:
        self.__id = id

    def setName(self, name: str) -> None:
        self.__name = name

    def setAddress(self, address: Address) -> None:
        self.__address = address

    def setAddress(self, street, houseNumber, city, postCode, country) -> None:
        address = Address()
        address.setStreet(street or "")
        address.setHouseNumber(houseNumber or "")
        address.setCity(city or "")
        address.setPostCode(postCode or "")
        address.setCountry(country or "")
        self.__address = address

    def setDescription(self, description) -> None:
        self.__description = description

    def setActive(self, isActive) -> None:
        self.__isActive = isActive

    def setModules(self, modules: List[Module]) -> None:
        self.__modules = modules

    def setLogoPath(self, logo_path: str) -> None:
        self.__logo_path = logo_path

# Other methods
    def getDataObject(self) -> dict:
        dataObject = {
            "id": self.getId(),
            "name": self.getName(),
            "address": self.getAddress(),
            "description": self.getDescription(),
            "modules": self.getModules(),
            "logo_path": self.getLogoPath()  # Include logo path in data object
        }
        return dataObject