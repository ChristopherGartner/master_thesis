from .AddressMapper import AddressMapper
from .Address import Address
from typing import List
from ..db.Database import Database

# holds and provides all address objects
class AddressRepository:
    __addresses     = []
    __addressMapper = None

# Get methods
    def getAddresses(self, db: Database) -> List[Address]:
        # if the addresses aren't loaded yet, they should be loaded.
        if len(self.__addresses) == 0:
            self.setAddresses(self.getAddressMapper().getAddressObjects(db))
        return self.__addresses

    def getAddressMapper(self) -> AddressMapper:
        if self.__addressMapper is None:
            self.__addressMapper = AddressMapper()
        return self.__addressMapper

    # saves address object and returns id of saved object
    def saveAddressObject(self, addressObject: Address, db: Database) -> int:
        return self.getAddressMapper().saveAddressObject(addressObject, db)

# Set methods
    def setAddresses(self, addresses: List[Address]) -> None:
        self.__addresses = addresses

    def setAddressMapper(self, addressMapper: AddressMapper) -> None:
        self.__addressMapper = addressMapper

