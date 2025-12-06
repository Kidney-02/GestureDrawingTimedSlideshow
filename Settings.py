
from PySide6.QtCore import QSettings

class Settings():
    def __init__(self,):
        super().__init__()

        self.settings = QSettings("KidneyCorps", "Drawing Practicer")


    def settings_load(self):
        """Loads settings from QSettings."""
        
        if self.settings is not None:
            return self.settings
        else:
            return None
       

    def settings_save(self, args:dict = None):
        """Saves window Settings"""
        
        for key, value in args.items():
            self.settings.setValue(key, value)

