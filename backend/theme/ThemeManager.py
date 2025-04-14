from typing import List
from flask import Flask
from ..io.TextfileManager import TextfileManager
import os


class ThemeManager:
    FOLDER_PATH_THEMES = "\\files\\themes"

    THEME_DEFAULT = "default"
    THEME_DARK    = "dark"
    THEME_BRIGHT  = "bright"
    THEME_MINIMAL = "minimal"
    THEME_NATURAL = "natural"
    THEME_NEON    = "neon"
    THEME_PLAYFUL = "playful"
    THEME_W11     = "w11"

    __themes = [
        THEME_DEFAULT,
        THEME_DARK,
        THEME_BRIGHT,
        THEME_MINIMAL,
        THEME_NATURAL,
        THEME_NEON,
        THEME_PLAYFUL,
        THEME_W11
    ]

    def getThemes(self) -> List[str]:
        return self.__themes

    def getThemeValues(self, theme: str, app: Flask) -> dict:
        textfile_manager = TextfileManager()
        file_path = os.path.join(app.static_folder, self.FOLDER_PATH_THEMES.lstrip(os.sep), f"{theme}.txt")
        if not os.path.exists(file_path):
            file_path = os.path.join(app.static_folder, self.FOLDER_PATH_THEMES.lstrip(os.sep),
                                     f"{self.THEME_DEFAULT}.txt")
        return textfile_manager.getKeyValueValueDict(file_path)