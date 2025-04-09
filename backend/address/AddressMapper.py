from typing import List
from .Address import *
from backend.db.Database import *

# loads the addresses from the database and
# creates address objects from them
class AddressMapper:

    __addressObjects = []

    def getAddressObjects(self, db: Database, rebuildObjects: bool = False) -> List[Address]:
        # Check if list is already initialized. If yes, skip refilling for performance reasons
        if len(self.__addressObjects) == 0 or rebuildObjects == True:
            self.__addressObjects = []

            selectedAddresses = db.execute(
                f"SELECT address.id, address.streetName, address.houseNumber, city.name AS cityName, city.postCode, country.name AS countryName "
                f"FROM address "
                f"INNER JOIN city ON address.fk_city = city.id "
                f"INNER JOIN country ON city.fk_country = country.id"
            )

            # create address objects
            for addressTuple in selectedAddresses:
                addressObject = Address()

                addressObject.setId(addressTuple[0])
                addressObject.setStreet(addressTuple[1])
                addressObject.setHouseNumber(addressTuple[2])
                addressObject.setCity(addressTuple[3])
                addressObject.setPostCode(addressTuple[4])
                addressObject.setCountry(addressTuple[5])

                self.__addressObjects.append(addressObject)

        return self.__addressObjects

    def __getCountryId(self, countryName: str, db: Database) -> int|None:
        result = db.execute(
            f"SELECT country.id FROM country WHERE name='{countryName}'"
        )

        # Check, whether result exists and extract id
        if result and len(result) > 0:
            return result[0][0]
        return None

    def __saveCountry(self, countryName: str, db: Database) -> None:
        db.execute(
            f"INSERT INTO country (country.name) VALUES ('{countryName}')",
            commit=True
        )

    def __getCityId(self, fk_country: int, cityName: str, postCode: str, db: Database) -> int|None:
        result = db.execute(
            f"SELECT city.id FROM city WHERE city.fk_country = '{fk_country}' "
            f"AND city.name = '{cityName}' "
            f"AND city.postcode = '{postCode}'"
        )

        # Check, whether result exists and extract id
        if result and len(result) > 0:
            return result[0][0]
        return None

    def __saveCity(self, fk_country: int, name: str, postCode: str, db: Database) -> None:
        db.execute(
            f"INSERT INTO city (fk_country, name, postcode) VALUES ({fk_country}, '{name}', '{postCode}')",
            commit=True
        )

    def __getAddress(self, fk_city: int, streetName: str, houseNumber: str, db: Database) -> bool:
        return db.execute(
            f"SELECT * FROM address WHERE address.fk_city = {fk_city} "
            f"AND address.streetName = '{streetName}' "
            f"AND address.houseNumber = '{houseNumber}'"
        )

    def __saveAddress(self, fk_city: int, streetName: str, houseNumber: str, db: Database) -> None:
        db.execute(
            f"INSERT INTO address (fk_city, streetName, houseNumber) VALUES ({fk_city}, '{streetName}', '{houseNumber}')",
            commit=True
        )

    def __getAddressId(self, fk_city: int, streetName: str, houseNumber: str, db: Database) -> int|None:
        result = db.execute(
            f"SELECT address.id FROM address WHERE address.fk_city = {fk_city} "
            f"AND address.streetName = '{streetName}' "
            f"AND address.houseNumber = '{houseNumber}'"
        )

        # Check, whether result exists and extract id
        if result and len(result) > 0:
            return result[0][0]
        return None


    # Saves an address object and returns it's ID as value
    def saveAddressObject(self, address: Address, db: Database) -> int:
        countryId = self.__getCountryId(address.getCountry(), db)
        if not countryId:
            self.__saveCountry(address.getCountry(), db)
            countryId = self.__getCountryId(address.getCountry(), db)

        cityId = self.__getCityId(countryId, address.getCity(), address.getPostCode(), db)
        if not cityId:
            self.__saveCity(countryId, address.getCity(), address.getPostCode(), db)
            cityId = self.__getCityId(countryId, address.getCity(), address.getPostCode(), db)

        if not self.__getAddress(cityId, address.getStreet(), address.getHouseNumber(), db):
            self.__saveAddress(cityId, address.getStreet(), address.getHouseNumber(), db)

        # Rebuild all objects to maintain this list valid
        self.getAddressObjects(db, True)

        return self.__getAddressId(cityId, address.getStreet(), address.getHouseNumber(), db)







