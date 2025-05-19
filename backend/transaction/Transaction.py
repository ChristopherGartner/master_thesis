from datetime import datetime
from ..address.Address import Address

class Transaction:
    __id = None
    __user_id = None
    __campsite_id = None
    __module_id = None
    __price = None
    __moneyCurrency = None
    __dateOfTransaction = None

    # Get methods
    def getId(self) -> int:
        return self.__id

    def getUserId(self) -> int:
        return self.__user_id

    def getCampsiteId(self) -> int:
        return self.__campsite_id

    def getModuleId(self) -> int:
        return self.__module_id

    def getPrice(self) -> float:
        return self.__price

    def getMoneyCurrency(self) -> str:
        return self.__moneyCurrency

    def getDateOfTransaction(self) -> datetime:
        return self.__dateOfTransaction

    # Set methods
    def setId(self, id: int) -> None:
        self.__id = int(id) if id is not None else None

    def setUserId(self, user_id: int) -> None:
        self.__user_id = int(user_id) if user_id is not None else None

    def setCampsiteId(self, campsite_id: int) -> None:
        self.__campsite_id = int(campsite_id) if campsite_id is not None else None

    def setModuleId(self, module_id: int) -> None:
        self.__module_id = int(module_id) if module_id is not None else None

    def setPrice(self, price: float) -> None:
        self.__price = float(price) if price is not None else None

    def setMoneyCurrency(self, moneyCurrency: str) -> None:
        self.__moneyCurrency = moneyCurrency

    def setDateOfTransaction(self, dateOfTransaction: datetime) -> None:
        self.__dateOfTransaction = dateOfTransaction

    # Other methods
    def getDataObject(self) -> dict:
        return {
            "id": self.getId(),
            "user_id": self.getUserId(),
            "campsite_id": self.getCampsiteId(),
            "module_id": self.getModuleId(),
            "price": self.getPrice(),
            "moneyCurrency": self.getMoneyCurrency(),
            "dateOfTransaction": self.getDateOfTransaction()
        }