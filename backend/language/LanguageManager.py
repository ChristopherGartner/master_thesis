from typing import List

from flask import Flask

from ..io.TextfileManager import TextfileManager
import os

# class used for managing multi language support
class LanguageManager:

    FOLDER_PATH_LANGUAGES = "\\files\\language" # path, where the language files lay in the static folder

    LANGUAGE_GERMAN          = "de_DE" # basic german language
    LANGUAGE_ENGLISH_ENGLISH = "en_EN" # basic british english language
    LANGUAGE_FRENCH_FRENCH   = "fr_FR" # basic french language
    LANGUAGE_SPAIN           = "sp_SP" # basic spain language
    LANGUAGE_ITALIAN         = "it_IT" # basic italian language
    LANGUAGE_DUTCH           = "nl_NL" # basic dutch language

    __languages = [
        LANGUAGE_GERMAN,
        LANGUAGE_ENGLISH_ENGLISH,
        LANGUAGE_FRENCH_FRENCH,
        LANGUAGE_SPAIN,
        LANGUAGE_ITALIAN,
        LANGUAGE_DUTCH,
    ]

# Get methods
    def getLanguages(self) -> List[str]:
        return self.__languages

# Other methods
    # returns the values for given language. Use class constants like "LANGUAGE_GERMAN" for accessing the language
    def getLanguageValues(self, language: str, app: Flask) -> dict:
        textfileManager = TextfileManager()
        filePath = os.path.join(app.static_folder, LanguageManager.FOLDER_PATH_LANGUAGES.lstrip(os.sep),
                                f"{language}.txt")
        if not os.path.exists(filePath):
            filePath = os.path.join(app.static_folder, LanguageManager.FOLDER_PATH_LANGUAGES.lstrip(os.sep),
                f"{LanguageManager.LANGUAGE_ENGLISH_ENGLISH}.txt")
        return textfileManager.getKeyValueValueDict(filePath)


