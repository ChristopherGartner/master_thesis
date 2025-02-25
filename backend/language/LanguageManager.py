from typing import List

from flask import Flask

from ..io.TextfileManager import TextfileManager
import os

# class used for managing multi language support
class LanguageManager:

    FOLDER_PATH_LANGUAGES = "\\files\\language" # path, where the language files lay in the static folder

    LANGUAGE_GERMAN          = "de_DE" # basic german language
    LANGUAGE_ENGLISH_ENGLISH = "en_EN" # basic british english language

    __languages = [
        LANGUAGE_GERMAN,
        LANGUAGE_ENGLISH_ENGLISH,
    ]

# Get methods
    def getLanguages(self) -> List[str]:
        return self.__languages

# Other methods
    # returns the values for given language. Use class constants like "LANGUAGE_GERMAN" for accessing the language
    def getLanguageValues(self, language: str, app: Flask):
        textfileManager = TextfileManager()

        filePath = os.path.join(app.static_folder + LanguageManager.FOLDER_PATH_LANGUAGES + "\\" + language + ".txt")

        return textfileManager.getKeyValueValueDict(filePath)


