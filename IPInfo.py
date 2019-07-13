import locale

import requests
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal
import base64
import localization


class IPSignals(QObject):
    infoSignal = pyqtSignal(dict)


class IPInfo(QRunnable):
    def __init__(self, ip, name):
        super().__init__()
        self.ip = ip
        self.ESO = name
        self.lang = list(locale.getdefaultlocale())[0][0:2]
        self.signals = IPSignals()
        if self.lang == "ru":
            self.loc = localization.ru
        else:
            self.loc = localization.en

    def getJSON(self, URL, params=None):
        r = requests.get(URL, params=params, timeout=10)
        return r.json()

    def run(self):
        try:
            info = self.getJSON("http://api.sypexgeo.net/json/" + self.ip)
            if info["country"] is None or info["country"][self.loc["country"]] == "":
                country = self.loc["unknown"]
                flag = b""
            else:
                country = info["country"][self.loc["country"]]
                flag = (
                    requests.get("https://www.countryflags.io/" + info["country"]["iso"] + "/flat/16.png").content
                    
                )

            if info["city"] is None or info["city"][self.loc["country"]] == "":
                city = self.loc["unknown"]
            else:
                city = info["city"][self.loc["country"]]
            self.signals.infoSignal.emit(
                {
                    "IP": str(self.ip),
                    "Country": country,
                    "City": city,
                    "Flag": base64.encodestring(flag).decode('ascii'),
                    "Name": self.ESO,
                }
            )
        except:
            pass
