from .CampsiteMapper import CampsiteMapper
from typing import List
from .Campsite import Campsite

# holds and provides all campsite objects
class CampsiteRepository:
    __campsites = []
    __campsiteMapper = None

# Get methods
    def getCampsites(self):
        # if the campsites aren't loaded yet, they should be loaded.
        if len(self.__campsites) == 0:
            self.setCampsites(self.getCampsiteMapper().getCampsiteObjects())
        return self.__campsites

    def getCampsiteMapper(self):
        if self.__campsiteMapper is None:
            self.__campsiteMapper = CampsiteMapper()
        return self.__campsiteMapper

    def getCampsitesAsDataObjects(self):
        campsiteDataObjects = []

        for campsite in self.getCampsites():
            campsiteDataObjects.append(campsite.getDataObject())

        return campsiteDataObjects

    # Set methods
    def setCampsites(self, campsites: List[Campsite]):
        self.__campsites = campsites

    def setCampsiteMapper(self, campSiteMapper: CampsiteMapper):
        self.__campsiteMapper = campSiteMapper
