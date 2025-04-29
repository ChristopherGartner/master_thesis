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
    __logo_path   = None

    # Features
    __feature_wlan            = False
    __feature_swimming        = False
    __feature_shower          = False
    __feature_playground      = False
    __feature_paw             = False
    __feature_parking         = False
    __feature_fishing         = False
    __feature_electricCurrent = False

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

    def getFeature_wlan(self) -> bool:
        return self.__feature_wlan

    def getFeature_swimming(self) -> bool:
        return self.__feature_swimming

    def getFeature_shower(self) -> bool:
        return self.__feature_shower

    def getFeature_playground(self) -> bool:
        return self.__feature_playground

    def getFeature_paw(self) -> bool:
        return self.__feature_paw

    def getFeature_parking(self) -> bool:
        return self.__feature_parking

    def getFeature_fishing(self) -> bool:
        return self.__feature_fishing

    def getFeature_electricCurrent(self) -> bool:
        return self.__feature_electricCurrent

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

    def setFeature_wlan(self, feature_wlan: bool) -> None:
        self.__feature_wlan = feature_wlan

    def setFeature_swimming(self, feature_swimming: bool) -> None:
        self.__feature_swimming = feature_swimming

    def setFeature_shower(self, feature_shower: bool) -> None:
        self.__feature_shower = feature_shower

    def setFeature_playground(self, feature_playground: bool) -> None:
        self.__feature_playground = feature_playground

    def setFeature_paw(self, feature_paw: bool) -> None:
        self.__feature_paw = feature_paw

    def setFeature_parking(self, feature_parking: bool) -> None:
        self.__feature_parking = feature_parking

    def setFeature_fishing(self, feature_fishing: bool) -> None:
        self.__feature_fishing = feature_fishing

    def setFeature_electricCurrent(self, feature_electricCurrent: bool) -> None:
        self.__feature_electricCurrent = feature_electricCurrent

# Other methods
    def getDataObject(self) -> dict:
        dataObject = {
            "id": self.getId(),
            "name": self.getName(),
            "address": self.getAddress(),
            "description": self.getDescription(),
            "modules": self.getModules(),
            "logo_path": self.getLogoPath()
        }
        return dataObject

    def getAllFeatures(self) -> List[str]:
        features = []

        if self.getFeature_wlan():
            features.append("wlan")

        if self.getFeature_paw():
            features.append("paw")

        if self.getFeature_shower():
            features.append("shower")

        if self.getFeature_playground():
            features.append("playground")

        if self.getFeature_electricCurrent():
            features.append("electricCurrent")

        if self.getFeature_parking():
            features.append("parking")

        if self.getFeature_swimming():
            features.append("swimming")

        if self.getFeature_fishing():
            features.append("fishing")

        return features
