from .Campsite import *
# loads the campsites from the database and
# creates Campsites objects from them
class CampsiteMapper:

    CAMPSITEDATA = [
        ['campsite_1', 'Fooname 1', 'FooStreet 1'],
        ['campsite_2', 'Fooname 2', 'FooStreet 2'],
        ['campsite_3', 'Fooname 3', 'FooStreet 3']
    ]

    __campSiteObjects = []

    # TODO Logic needs to be reimplemented when database
    # TODO is integrated to read off the data out of the database
    #
    # Loads the campsite data from the database and creates campsite
    # objects out of it.
    #
    # @param rebuildObjects = Boolean whether the campsite objects should be rebuilt
    def getCampsiteObjects(self, rebuildObjects: bool = False):
        # Check if list is already initialized. If yes, skip refilling for performance reasons
        if len(self.__campSiteObjects) == 0 or rebuildObjects == True:
            for campsite in self.CAMPSITEDATA:
                campSiteObject = Campsite()
                campSiteObject.setId(campsite[0])
                campSiteObject.setName(campsite[1])
                campSiteObject.setAddress(campsite[2])

                self.__campSiteObjects.append(campSiteObject)

        return self.__campSiteObjects



