
from PySide6.QtCore import QSettings

class Settings():
    def __init__(self,):
        super().__init__()


        self.settings = QSettings("orgName", "appName")




    def settings_load(self):
        """Loads settings from QSettings."""
        
        if self.settings is not None:

            return self.settings
            


            # self.restoreGeometry(self.settings.value("geometry"))
            # self.count = self.settings.value("count")
            # self.time = self.settings.value("time")

        else:
            # Default settings

            args = {
                "geometry": (100, 100, 700, 500),
                "count": 10,
                "time": 10,

            }
            # self.setGeometry(100, 100, 700, 500) 
            # self.count = 10
            # self.time = 10


            

    def settings_save(self, args:dict = None):
        """Saves window Settings"""
        
        for key, value in args.items():
            self.settings.setValue(key, value)
            # print(f"Key: {key}, Value: {value}")
        
        
        # self.settings.setValue("geometry", self.saveGeometry())
        # self.settings.setValue("count", self.count_input.text())
        # self.settings.setValue("time", self.time_input.text())


