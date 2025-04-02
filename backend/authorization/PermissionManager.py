from typing import List, Dict
from ..io.TextfileManager import TextfileManager
import os
from flask import Flask

class PermissionManager:
    AUTHORIZATION_FOLDER = "\\files\\authorization"
    PERMISSIONS_FILE = "permissions.txt"
    GROUPS_FILE = "groups.txt"

    __textFileManager = None
    __app = None
    __permissions = None
    __groups = None

    def __init__(self, app: Flask):
        self.__textFileManager = TextfileManager()
        self.__app = app
        self.__permissions = self._loadPermissions()
        self.__groups = self._loadGroups()

    def _loadPermissions(self) -> List[str]:
        filepath = os.path.join(self.__app.static_folder + self.AUTHORIZATION_FOLDER, self.PERMISSIONS_FILE)
        return self.__textFileManager.getAsList(filepath)

    def _loadGroups(self) -> Dict[str, List[str]]:
        filepath = os.path.join(self.__app.static_folder + self.AUTHORIZATION_FOLDER, self.GROUPS_FILE)
        return self.__textFileManager.getKeyValueValueDict(filepath, ",")

    # Returns the permissions of a certain group
    def getGroupPermissions(self, group: str) -> List[str]:
        return self.__groups.get(group, [])