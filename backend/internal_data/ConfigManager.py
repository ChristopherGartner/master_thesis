from flask import Flask

from ..io.TextfileManager import TextfileManager
import os

""" Maintains all config file related things """
class ConfigManager:

    __configFileDict = dict()

    CONFIG_FILE_PATH = "\\backend\\internal_data\\config.txt"

    """Returns all config file keys and values. Needs to be seperated by '=' in order to work"""
    def getConfigValues(self, app: Flask) -> dict:

        if not self.__configFileDict:
            textfileManager = TextfileManager()
            filePath = os.path.join(app.root_path + ConfigManager.CONFIG_FILE_PATH)

            self.__configFileDict = textfileManager.getKeyValueValueDict(filePath)

        return self.__configFileDict

    def overrideDBargs(self, args: dict):
        for a in args:
            self.__configFileDict[a] = args[a]

