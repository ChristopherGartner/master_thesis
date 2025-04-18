from typing import List
from flask import Flask
from ..io.TextfileManager import TextfileManager
import os

class ThemeManager:
    FOLDER_PATH_THEMES = "\\files\\themes"

    KEY_IS_LIGHT_THEME = "isLightTheme"

    # Admin Themes
    THEME_ADMIN = "admin"

    # Normal Themes
    THEME_DEFAULT  = "default"
    THEME_DARK     = "dark"
    THEME_BRIGHT   = "bright"
    THEME_MINIMAL  = "minimal"
    THEME_NATURAL  = "natural"
    THEME_NEON     = "neon"
    THEME_PLAYFUL  = "playful"
    THEME_W11      = "w11"
    THEME_W11_DARK = "w11_dark"

    __themes = [
        THEME_ADMIN,
        THEME_DEFAULT,
        THEME_DARK,
        THEME_BRIGHT,
        THEME_MINIMAL,
        THEME_NATURAL,
        THEME_NEON,
        THEME_PLAYFUL,
        THEME_W11,
        THEME_W11_DARK,
    ]

    def getThemes(self) -> List[str]:
        return self.__themes

    def getThemeValues(self, theme: str, app: Flask) -> dict:
        textfile_manager = TextfileManager()
        file_path = os.path.join(app.static_folder, self.FOLDER_PATH_THEMES.lstrip(os.sep), f"{theme}.txt")
        if not os.path.exists(file_path):
            file_path = os.path.join(app.static_folder, self.FOLDER_PATH_THEMES.lstrip(os.sep), f"{self.THEME_DEFAULT}.txt")
        theme_values = textfile_manager.getKeyValueValueDict(file_path)
        # Convert isLightTheme to boolean (for potential future use)
        if self.KEY_IS_LIGHT_THEME in theme_values:
            theme_values[self.KEY_IS_LIGHT_THEME] = theme_values[self.KEY_IS_LIGHT_THEME].lower() == 'true'
        else:
            theme_values[self.KEY_IS_LIGHT_THEME] = True  # Fallback to True
        app.logger.info(f"Loaded theme {theme}: isLightTheme={theme_values[self.KEY_IS_LIGHT_THEME]} (used for theme adjustments)")
        return theme_values