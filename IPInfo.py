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
        self.signals = IPSignals()

    def getJSON(self, URL, params=None):
        r = requests.get(URL, params=params, timeout=10)
        return r.json()

    def run(self):
        try:
            info = self.getJSON("https://www.ipqualityscore.com/api/json/ip/AGb3QZuZgJ9Z6l5n00Eym9k9VMKS2ETi/"+self.ip+ "?strictness=1&allow_public_access_points=true")
            if info["success"]:
                if info["country_code"] == "-":
                    flag = b""
                else:
                    flag = (
                        requests.get("https://www.countryflags.io/" + info["country_code"] + "/flat/16.png").content
                        
                    )
                country = info["country_code"]
                city = info["city"]
                timezone = info["timezone"]
                fraud_score = info["proxy"]
                ISP = info["ISP"]
                self.signals.infoSignal.emit(
                    {
                        "IP": str(self.ip),
                        "Country": country,
                        "City": city,
                        "ISP": ISP,
                        "timezone": timezone,
                        "fraud_score": fraud_score,
                        "Flag": base64.encodestring(flag).decode('ascii'),
                        "Name": self.ESO,
                    }
                )
        except:
            pass
