import ipaddress
import json
import locale
import os
import os.path
import pkgutil
import random
import string
import struct
import sys
import winreg
import xml.etree.ElementTree as ElementTree
from datetime import datetime, timezone

import requests
from dateutil.parser import parse
from googletrans import Translator
from gtts import gTTS
from PyQt5.QtCore import (
    QObject,
    QRunnable,
    Qt,
    QThread,
    QThreadPool,
    QTimer,
    pyqtSignal,
)
from PyQt5.QtGui import QColor, QFont, QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QDesktopWidget,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QWidget,
    QGroupBox,
)
from scapy.all import sniff, traceroute
from scapy.layers.inet import IP, TCP, UDP

import localization
from playsound import playsound

clBlack = "black"
clViolet = "#B44DD8"
clBlue = "#56A7E2"
clGreen = "#18AD11"
clRed = "#D84D4D"


class LobbySignals(QObject):
    playerinLobby = pyqtSignal(dict)


class pingIP(QRunnable):
    def __init__(self, ip):
        super().__init__()
        self.ip = ip
        self.signals = LobbySignals()

    def run(self):
        result, _ = traceroute(self.ip)

        # r = [(snd, recv) for snd, recv in result if snd.dst == self.ip]
        maxttl = max(result, key=lambda x: x[0].ttl)[0].ttl
        stat = [(snd, recv) for snd, recv in result if snd.ttl == maxttl]
        self.signals.playerinLobby.emit(
            {
                "IP": stat[0][0].dst,
                "RTT": f"{round(1000*(stat[0][1].time - stat[0][0].sent_time))} ms",
            }
        )
        print(
            f"IP: {stat[0][0].dst} ttl: {stat[0][0].ttl} rtt: {round(1000*(stat[0][1].time - stat[0][0].sent_time))}"
        )


class justSpeech(QRunnable):
    def __init__(self, text):
        super().__init__()
        self.text = text
        self.lang = list(locale.getdefaultlocale())[0][0:2]

        if self.lang == "ru":
            self.loc = localization.ru
        else:
            self.loc = localization.en

    def getSoundsPath(self):
        if getattr(sys, "frozen", False):
            # we are running in a bundle
            return os.path.join(sys._MEIPASS, "sound")
        else:
            # we are running in a normal Python environment
            return os.path.dirname(os.path.abspath(__file__))

    def run(self):
        try:
            soundPath = self.getSoundsPath()
            playsound(os.path.join(soundPath, "connect.mp3"))
            tts = gTTS(self.text, lang=self.loc["language"])
            sound = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=32)
            )
            tts.save(os.path.join("TTS", sound + ".mp3"))

            playsound(os.path.join("TTS", sound + ".mp3"))
        except Exception as e:
            print(e)


class translateAndSpeech2(QRunnable):
    def __init__(self, text):
        super().__init__()
        self.text = text
        self.lang = list(locale.getdefaultlocale())[0][0:2]

        if self.lang == "ru":
            self.loc = localization.ru
        else:
            self.loc = localization.en

    def getSoundsPath(self):
        if getattr(sys, "frozen", False):
            # we are running in a bundle
            return os.path.join(sys._MEIPASS, "sound")
        else:
            # we are running in a normal Python environment
            return os.path.dirname(os.path.abspath(__file__))

    def run(self):
        try:
            # notif sound
            soundPath = self.getSoundsPath()
            playsound(os.path.join(soundPath, "message.mp3"))
            # if text language is not native -> translate it
            translator = Translator()
            detected_lang = translator.detect(self.text).lang
            if detected_lang != self.lang:
                self.text = translator.translate(self.text, dest=self.lang).text
            tts = gTTS(self.text, lang=self.lang)
            sound = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=32)
            )
            tts.save(os.path.join("TTS", sound + ".mp3"))

            playsound(os.path.join("TTS", sound + ".mp3"))
        except Exception as e:
            print(e)


class translateAndSpeech(QRunnable):
    def __init__(self, who, text):
        super().__init__()
        self.who = who
        self.text = text
        self.lang = list(locale.getdefaultlocale())[0][0:2]

        if self.lang == "ru":
            self.loc = localization.ru
        else:
            self.loc = localization.en

    def getSoundsPath(self):
        if getattr(sys, "frozen", False):
            # we are running in a bundle
            return os.path.join(sys._MEIPASS, "sound")
        else:
            # we are running in a normal Python environment
            return os.path.dirname(os.path.abspath(__file__))

    def run(self):
        try:
            # notif sound
            soundPath = self.getSoundsPath()
            playsound(os.path.join(soundPath, "message.mp3"), block=False)
            # if text language is not native -> translate it
            translator = Translator()
            detected_lang = translator.detect(self.text).lang
            if detected_lang != self.lang:
                self.text = translator.translate(self.text, dest=self.lang).text
            tts = gTTS(self.text, lang=self.lang)
            sound = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=32)
            )
            tts.save(os.path.join("TTS", sound + ".mp3"))

            tts2 = gTTS(self.who, lang=self.loc["language"])
            sound2 = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=32)
            )
            tts2.save(os.path.join("TTS", sound2 + ".mp3"))

            playsound(os.path.join("TTS", sound2 + ".mp3"))
            playsound(os.path.join("TTS", sound + ".mp3"))

        except Exception as e:
            print(e)


class SniffThread(QThread):
    DataToUpdate = pyqtSignal(tuple)
    activeIP = pyqtSignal(str)
    IPandESO = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.pool = QThreadPool()

    def getGamePath(self):
        try:
            registry_key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\microsoft games\age of empires 3 expansion pack 2\1.0",
                0,
                winreg.KEY_READ,
            )
            value, _ = winreg.QueryValueEx(registry_key, "setuppath")
            winreg.CloseKey(registry_key)
            return value
        except WindowsError:
            return None

    def playTaunt(self, name):
        gamePath = self.getGamePath()
        if gamePath is not None:
            try:
                playsound(os.path.join(gamePath, "Sound", "Taunts", name), block=False)
            except:
                pass

    def getSoundsPath(self):
        if getattr(sys, "frozen", False):
            # we are running in a bundle
            return os.path.join(sys._MEIPASS, "sound")
        else:
            # we are running in a normal Python environment
            return os.path.dirname(os.path.abspath(__file__))

    def utc_to_local(self, utc_dt):
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

    def printWithLog(self, msg):
        print(msg, flush=True)
        with open("log.txt", "a+", encoding="utf-8") as f:
            print(msg, file=f, flush=True)

    def ColoredOutput(self, text, cType):
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if cType == 0:
            return f"{dt} : {text}", clBlack
        if cType == 1:
            return f"{dt} : {text}", clViolet
        if cType == 2:
            return f"{dt} : {text}", clBlue
        if cType == 3:
            return f"{dt} : {text}", clGreen
        if cType == 4:
            return f"{dt} : {text}", clRed

    def getJSON(self, URL, params=None):
        r = requests.get(URL, params=params, timeout=10)
        return r.json()

    def getXML(self, URL, params):
        r = requests.get(URL, params=params, timeout=10)
        return ElementTree.fromstring(r.text)

    def find_between(self, s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""

    def SniffCallback(self, packet):

        if packet.haslayer(UDP):
            srcIP = packet[IP].src
            dstIP = packet[IP].dst
            data = bytes(packet[UDP].payload)
            try:
                if srcIP != "168.61.152.225" and dstIP != "168.61.152.225":

                    # Get IP of connected player
                    if not ipaddress.ip_address(srcIP).is_private:
                        self.activeIP.emit(srcIP)

                    if not ipaddress.ip_address(dstIP).is_private:
                        self.activeIP.emit(dstIP)
                ############################
                if len(data) > 0:
                    if (
                        data[0] == 0x03
                        and data[8] == 0x01
                        and data[9] == 0x01
                        and data[10] == 0x03
                    ):

                        text = data[15:-8].decode("UTF-16le")
                        if text.find("/--flare ") == 0:
                            return

                        if ipaddress.ip_address(srcIP).is_private:
                            if text.find("/--taunt ") != 0:
                                self.DataToUpdate.emit(
                                    self.ColoredOutput(
                                        self.loc["yousay"].format(dst=dstIP, text=text),
                                        2,
                                    )
                                )
                            else:
                                self.DataToUpdate.emit(
                                    self.ColoredOutput(
                                        self.loc["yousaytaunt"].format(
                                            dst=dstIP,
                                            text=self.find_between(
                                                text, "/--taunt ", ".mp3"
                                            ),
                                        ),
                                        2,
                                    )
                                )
                        else:
                            if text.find("/--taunt ") != 0:
                                self.DataToUpdate.emit(
                                    self.ColoredOutput(
                                        self.loc["playersay"].format(
                                            src=srcIP, text=text
                                        ),
                                        3,
                                    )
                                )
                                thread = translateAndSpeech2(text)
                                self.pool.start(thread)

                            else:
                                self.DataToUpdate.emit(
                                    self.ColoredOutput(
                                        self.loc["playersaytaunt"].format(
                                            src=srcIP,
                                            text=self.find_between(
                                                text, "/--taunt ", ".mp3"
                                            ),
                                        ),
                                        3,
                                    )
                                )

                                self.playTaunt(text[9:])

            except Exception as e:
                self.DataToUpdate.emit(self.ColoredOutput(str(e) + "\n" + str(data), 4))
        if packet.haslayer(TCP):
            if packet[TCP].payload is not None:
                data = packet[TCP].payload
                try:
                    start = bytes(data).find(b"\x3c\x65\x73\x6f")
                    if start != -1:
                        end = bytes(data).find(b"\x3c\x2f\x65\x73\x6f\x3e", start)
                        if end != -1:
                            if start < end:
                                if -(len(bytes(data)) - end - 6) != 0:
                                    xml = str(
                                        bytes(data)[
                                            start : -(len(bytes(data)) - end - 6)
                                        ].decode("UTF-8")
                                    )
                                else:
                                    xml = str(bytes(data)[start:].decode("UTF-8"))

                                root = ElementTree.fromstring(xml)

                                ty = root.attrib["ty"]
                                tp = root.attrib["tp"]
                                g = root.find("./g")
                                c = root.find("./c")

                                if ty is not None and tp is not None:
                                    # Chats
                                    if c is not None:
                                        if ty is not None and tp is not None:
                                            # Close chat
                                            if (
                                                ty == "response"
                                                or ty == "request"
                                                or ty == "event"
                                            ) and tp == "leave":
                                                # Ignore request
                                                if ty == "request":
                                                    return
                                                # Leave event
                                                if ty == "event":
                                                    u = c.find("./u")
                                                    cn = c.attrib["n"]
                                                    un = u.attrib["n"]
                                                    self.DataToUpdate.emit(
                                                        self.ColoredOutput(
                                                            self.loc[
                                                                "playerleftchat"
                                                            ].format(un=un, cn=cn),
                                                            1,
                                                        )
                                                    )
                                                    return
                                                n = c.attrib["n"]
                                                self.DataToUpdate.emit(
                                                    self.ColoredOutput(
                                                        self.loc["youleftchat"].format(
                                                            n=n
                                                        ),
                                                        2,
                                                    )
                                                )
                                                return

                                            # Message to chat
                                            if (
                                                ty == "event" or ty == "request"
                                            ) and tp == "msg":
                                                cn = c.attrib["n"]
                                                if ty == "event":
                                                    u = c.find("./u")
                                                    un = u.attrib["n"]
                                                    m = u.find("./m")

                                                    self.DataToUpdate.emit(
                                                        self.ColoredOutput(
                                                            self.loc[
                                                                "playerwritechat"
                                                            ].format(
                                                                un=un, cn=cn, m=m.text
                                                            ),
                                                            1,
                                                        )
                                                    )
                                                    return
                                                else:
                                                    m = c.find("./m")
                                                    self.DataToUpdate.emit(
                                                        self.ColoredOutput(
                                                            self.loc[
                                                                "youwritechat"
                                                            ].format(cn=cn, m=m.text),
                                                            2,
                                                        )
                                                    )
                                                    return
                                            # Enter to chat browser
                                            if ty == "response" and tp == "list":
                                                self.DataToUpdate.emit(
                                                    self.ColoredOutput(
                                                        self.loc["updatedchatlist"], 2
                                                    )
                                                )
                                                return
                                            # Join to chat
                                            if (
                                                ty == "response"
                                                or ty == "request"
                                                or ty == "event"
                                            ) and tp == "join":
                                                # Ignore request
                                                if ty == "request":
                                                    return
                                                # Event join
                                                if ty == "event":
                                                    u = c.find("./u")
                                                    cn = c.attrib["n"]
                                                    un = u.attrib["n"]
                                                    self.DataToUpdate.emit(
                                                        self.ColoredOutput(
                                                            self.loc[
                                                                "playerjoinchat"
                                                            ].format(un=un, cn=cn),
                                                            1,
                                                        )
                                                    )
                                                    return
                                                n = c.attrib["n"]
                                                messages = []
                                                for item in c.findall("h"):
                                                    t = item.find("./t")
                                                    f = item.find("./f")
                                                    m = item.find("./m")
                                                    messages.append(
                                                        f.text
                                                        + " ["
                                                        + self.utc_to_local(
                                                            parse(t.text)
                                                        ).strftime("%d.%m.%y %H:%M:%S")
                                                        + "] : "
                                                        + m.text
                                                    )
                                                self.DataToUpdate.emit(
                                                    self.ColoredOutput(
                                                        self.loc["youjoinchat"].format(
                                                            n=n
                                                        )
                                                        + "\n"
                                                        + "\n".join(messages),
                                                        2,
                                                    )
                                                )
                                                return

                                    # Games
                                    if g is not None:
                                        if ty is not None and tp is not None:
                                            # Get invite
                                            if ty == "event" and tp == "invite":
                                                n = g.find("./n")
                                                u = g.find("./u")
                                                un = u.find("./n")
                                                st = g.find("./st")
                                                s10 = st.find("./s10")
                                                s38 = st.find("./s38")

                                                if s38 is not None:
                                                    start = 82
                                                else:
                                                    start = 71
                                                players = []
                                                for i, pstr in [
                                                    (i, "s" + str(start + 24 * i))
                                                    for i in range(8)
                                                ]:
                                                    if st.find("./" + pstr) is not None:
                                                        players.append(
                                                            st.find("./" + pstr).text
                                                        )
                                                playerstr = ", ".join(players)
                                                self.DataToUpdate.emit(
                                                    self.ColoredOutput(
                                                        self.loc["playerinvite"].format(
                                                            un=un.text,
                                                            n=n.text,
                                                            s10=s10.text,
                                                            playerstr=playerstr,
                                                        ),
                                                        2,
                                                    )
                                                )
                                                return
                                            # Lobby updated
                                            if ty == "response" and tp == "update":
                                                n = g.find("./n")
                                                st = g.find("./st")
                                                s10 = st.find("./s10")
                                                s38 = st.find("./s38")

                                                if s38 is not None:
                                                    start = 82
                                                else:
                                                    start = 71
                                                players = []
                                                for i, pstr in [
                                                    (i, "s" + str(start + 24 * i))
                                                    for i in range(8)
                                                ]:
                                                    if st.find("./" + pstr) is not None:
                                                        players.append(
                                                            st.find("./" + pstr).text
                                                        )
                                                playerstr = ", ".join(players)
                                                self.DataToUpdate.emit(
                                                    self.ColoredOutput(
                                                        self.loc["lobbyupdated"].format(
                                                            n=n.text,
                                                            s10=s10.text,
                                                            playerstr=playerstr,
                                                        ),
                                                        2,
                                                    )
                                                )
                                                return
                                            # Remove user
                                            if ty == "event" and tp == "removeuser":
                                                u = g.find("./u")
                                                n = u.find("./n")
                                                self.DataToUpdate.emit(
                                                    self.ColoredOutput(
                                                        self.loc[
                                                            "playerremoved"
                                                        ].format(n=n.text),
                                                        2,
                                                    )
                                                )
                                                return
                                            # Ignore connectusr (it duplicates message)
                                            if (
                                                ty == "request" or ty == "response"
                                            ) and tp == "connectusr":
                                                return
                                            # Create lobby
                                            if (
                                                ty == "request" or ty == "response"
                                            ) and tp == "add":
                                                if ty == "response":
                                                    return
                                                self.DataToUpdate.emit(
                                                    self.ColoredOutput(
                                                        self.loc["createlobby"], 2
                                                    )
                                                )
                                                return
                                            # Remove/ leave/ cancel
                                            if (
                                                ty == "request" or ty == "response"
                                            ) and (
                                                tp == "remove"
                                                or tp == "leave"
                                                or tp == "cancel"
                                            ):
                                                if ty == "response":
                                                    return
                                                self.DataToUpdate.emit(
                                                    self.ColoredOutput(
                                                        self.loc["youleftlobby"], 2
                                                    )
                                                )
                                                return
                                            # Someone connecting
                                            if (
                                                ty == "request" or ty == "response"
                                            ) and tp == "join":
                                                if ty == "response":
                                                    return
                                                u = g.find("./u")
                                                if u is not None:
                                                    n = u.find("./n")
                                                    xip = u.find("./xip")
                                                    if (
                                                        xip is not None
                                                        and n is not None
                                                    ):
                                                        pIP = ipaddress.IPv4Address(
                                                            struct.pack(
                                                                "<L", int(xip.text, 16)
                                                            )
                                                        )
                                                        self.IPandESO.emit(
                                                            {
                                                                "IP": str(pIP),
                                                                "ESO": n.text,
                                                            }
                                                        )
                                                        IPinfo = self.getJSON(
                                                            "http://api.sypexgeo.net/json/"
                                                            + str(pIP)
                                                        )
                                                        if IPinfo["country"] is None:
                                                            country = ""
                                                        else:
                                                            country = IPinfo["country"][
                                                                self.loc["country"]
                                                            ]
                                                        self.DataToUpdate.emit(
                                                            self.ColoredOutput(
                                                                self.loc[
                                                                    "playerconncet"
                                                                ].format(
                                                                    n=n.text,
                                                                    IP=pIP,
                                                                    country=country,
                                                                ),
                                                                3,
                                                            )
                                                        )
                                                        thread = justSpeech(
                                                            self.loc[
                                                                "playerconnectvoice"
                                                            ].format(
                                                                n=n.text,
                                                                country=country,
                                                            )
                                                        )
                                                        self.pool.start(thread)

                                                        return
                                    # Start QuickSearch
                                    if (
                                        ty == "response" or ty == "request"
                                    ) and tp == "begin":
                                        # Ignore request
                                        if ty == "request":
                                            return
                                        self.DataToUpdate.emit(
                                            self.ColoredOutput(self.loc["startqs"], 2)
                                        )
                                        return
                                    # Send invite
                                    if (
                                        ty == "response" or ty == "request"
                                    ) and tp == "invite":
                                        # Ignore response
                                        if ty == "response":
                                            return
                                        iu = root.find("./iu")
                                        self.DataToUpdate.emit(
                                            self.ColoredOutput(
                                                self.loc["youinvite"].format(
                                                    iu=iu.text
                                                ),
                                                2,
                                            )
                                        )
                                        return
                                    # Cancel QuickSearch
                                    if (
                                        ty == "response" or ty == "request"
                                    ) and tp == "cancel":
                                        # Ignore request
                                        if ty == "request":
                                            return
                                        self.DataToUpdate.emit(
                                            self.ColoredOutput(self.loc["cancelqs"], 2)
                                        )
                                        return
                                    # Remove player from list
                                    if (
                                        ty == "response" or ty == "request"
                                    ) and tp == "remove":
                                        # Ignore request
                                        if ty == "request":
                                            return
                                        user = root.find("user")
                                        if user is not None:
                                            name = user.find("name")
                                            self.DataToUpdate.emit(
                                                self.ColoredOutput(
                                                    self.loc["fflremove"].format(
                                                        name=name.text
                                                    ),
                                                    2,
                                                )
                                            )
                                            return
                                    # Add player to list
                                    if (
                                        ty == "response" or ty == "request"
                                    ) and tp == "add":
                                        # Ignore request
                                        if ty == "request":
                                            return
                                        user = root.find("user")
                                        if user is not None:
                                            n = user.find("n")
                                            if n is not None:
                                                b = user.attrib["b"]
                                                if b == "0":
                                                    self.DataToUpdate.emit(
                                                        self.ColoredOutput(
                                                            self.loc["fradded"].format(
                                                                n=n.text
                                                            ),
                                                            2,
                                                        )
                                                    )
                                                else:
                                                    self.DataToUpdate.emit(
                                                        self.ColoredOutput(
                                                            self.loc["fadded"].format(
                                                                n=n.text
                                                            ),
                                                            2,
                                                        )
                                                    )
                                                return
                                    # Update list
                                    if (
                                        ty == "response" or ty == "request"
                                    ) and tp == "update":
                                        # Ignore request
                                        if ty == "request":
                                            return
                                        user = root.find("user")
                                        if user is not None:
                                            name = user.find("name")
                                            blocked = user.attrib["blocked"]
                                            if blocked == "0":
                                                self.DataToUpdate.emit(
                                                    self.ColoredOutput(
                                                        self.loc["frmoved"].format(
                                                            name=name.text
                                                        ),
                                                        2,
                                                    )
                                                )
                                            else:
                                                self.DataToUpdate.emit(
                                                    self.ColoredOutput(
                                                        self.loc["fmoved"].format(
                                                            name=name.text
                                                        ),
                                                        2,
                                                    )
                                                )
                                            return
                                    # Player stat
                                    if ty == "request" and tp == "metaquery":
                                        return
                                    if (
                                        ty == "response" or ty == "request"
                                    ) and tp == "query":
                                        # Ignore request
                                        if ty == "request":
                                            return
                                        un = root.find("./un")
                                        pd = root.find("./pd")
                                        if un is not None and pd is not None:
                                            cd = pd.find("./cd")
                                            lld = pd.find("./lld")

                                            cn = pd.find("./cn")
                                            ca = pd.find("./ca")

                                            sg = pd.find("./sg")
                                            sw = pd.find("./sw")
                                            sp = pd.find("./sp")

                                            tg = pd.find("./tg")
                                            tw = pd.find("./tw")
                                            tp = pd.find("./tp")

                                            dg = pd.find("./dg")
                                            dw = pd.find("./dw")
                                            dp = pd.find("./dp")

                                            spts = pd.find("./spts")
                                            tpts = pd.find("./tpts")
                                            dpts = pd.find("./dpts")
                                            self.DataToUpdate.emit(
                                                self.ColoredOutput(
                                                    self.loc["stat"].format(un=un.text)
                                                    + self.loc["regdate"].format(
                                                        cd=cd.text
                                                    )
                                                    + self.loc["lastactive"].format(
                                                        lld=lld.text
                                                    )
                                                    + self.loc["clan"].format(
                                                        ca=ca.text, cn=cn.text
                                                    )
                                                    + self.loc["supremacy"].format(
                                                        sg=sg.text,
                                                        sw=sw.text,
                                                        sp=sp.text,
                                                        spts=spts.text,
                                                    )
                                                    + self.loc["treaty"].format(
                                                        tg=tg.text,
                                                        tw=tw.text,
                                                        tp=tp.text,
                                                        tpts=tpts.text,
                                                    )
                                                    + self.loc["dm"].format(
                                                        dg=dg.text,
                                                        dw=dw.text,
                                                        dp=dp.text,
                                                        dpts=dpts.text,
                                                    ),
                                                    1,
                                                )
                                            )
                                            return
                                    # Whisper to us
                                    if ty == "event" and tp == "whisper":
                                        user = root.find("./user")
                                        n = user.find("./n")
                                        w = user.find("./w")
                                        self.DataToUpdate.emit(
                                            self.ColoredOutput(
                                                self.loc["playerwhisper"].format(
                                                    n=n.text, w=w.text
                                                ),
                                                3,
                                            )
                                        )
                                        thread = translateAndSpeech(
                                            self.loc["playerwhispervoice"].format(
                                                n=n.text
                                            ),
                                            w.text,
                                        )
                                        self.pool.start(thread)

                                        return

                                    # we whisper
                                    if (
                                        ty == "request" or ty == "response"
                                    ) and tp == "whisper":
                                        if ty == "response":
                                            return
                                        user = root.find("./user")
                                        name = user.find("./name")
                                        whisper = user.find("./whisper")
                                        self.DataToUpdate.emit(
                                            self.ColoredOutput(
                                                self.loc["youwhisper"].format(
                                                    name=name.text, whisper=whisper.text
                                                ),
                                                2,
                                            )
                                        )
                                        return
                                    # List of lobbies
                                    if ty == "request" and tp == "list":
                                        self.DataToUpdate.emit(
                                            self.ColoredOutput(
                                                self.loc["listlobbyupdate"], 2
                                            )
                                        )
                                        return
                                    # Population ESO
                                    if ty == "event" and tp == "population":
                                        self.DataToUpdate.emit(
                                            self.ColoredOutput(
                                                self.loc["eso"].format(
                                                    num=root.find("./numPlayers").text
                                                ),
                                                1,
                                            )
                                        )
                                        return

                                    if ty == "event" and tp == "update":
                                        user = root.find("./user")
                                        pn = root.find("./pn")
                                        if pn is not None:
                                            ut = root.find("./ut")
                                            self.DataToUpdate.emit(
                                                self.ColoredOutput(
                                                    self.loc["qsupdated"].format(
                                                        ut=ut.text
                                                    ),
                                                    1,
                                                )
                                            )
                                            return
                                        # Friends
                                        if user is not None:
                                            n = user.find("./n")
                                            s = user.find("./s")
                                            m = user.find("./m")
                                            gid = user.find("./gid")
                                            if s.text == "offline":
                                                self.DataToUpdate.emit(
                                                    self.ColoredOutput(
                                                        self.loc["friendleft"].format(
                                                            n=n.text
                                                        ),
                                                        1,
                                                    )
                                                )
                                                return
                                            if m is not None and gid is not None:
                                                if gid.text == "1":
                                                    gt = self.loc["Vanilla"]
                                                else:
                                                    gt = self.loc["tad"]
                                                if m.text == "IG":
                                                    self.DataToUpdate.emit(
                                                        self.ColoredOutput(
                                                            self.loc[
                                                                "friendingame"
                                                            ].format(n=n.text, gt=gt),
                                                            1,
                                                        )
                                                    )
                                                    return
                                                else:
                                                    self.DataToUpdate.emit(
                                                        self.ColoredOutput(
                                                            self.loc[
                                                                "friendonline"
                                                            ].format(n=n.text, gt=gt),
                                                            3,
                                                        )
                                                    )
                                                    thread = justSpeech(
                                                        self.loc["friendonline"].format(
                                                            n=n.text, gt=gt
                                                        )
                                                    )
                                                    self.pool.start(thread)

                                                    return
                                            else:
                                                return
                                self.DataToUpdate.emit(self.ColoredOutput(xml, 0))
                except Exception as e:
                    self.DataToUpdate.emit(
                        self.ColoredOutput(str(e) + "\n" + str(data), 4)
                    )

    def run(self):
        self.lang = list(locale.getdefaultlocale())[0][0:2]

        if self.lang == "ru":
            self.loc = localization.ru
        else:
            self.loc = localization.en

        if not os.path.exists("TTS"):
            os.makedirs("TTS")
        sniff(prn=self.SniffCallback, filter="tcp port 2300 or udp port 2300", store=0)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()


    def getIconPath(self):
        if getattr(sys, "frozen", False):
            # we are running in a bundle
            return os.path.join(sys._MEIPASS, "icon.ico")
        else:
            # we are running in a normal Python environment
            return os.path.dirname(os.path.abspath(__file__))

    def initUI(self):
        self.jsonPackets = []
        self.jsonIPandNames = []
        self.IPinLobby = []
        self.pool = QThreadPool()
        grid = QGridLayout()
        self.setLayout(grid)
        self.w = QListWidget()
        self.w.setFont(QFont("Consolas", 11, weight=QFont.Bold))
        grid.addWidget(self.w, 1, 0)
        self.lobby = QListWidget()
        self.lobby.setFixedWidth(250)
        self.lobby.setFont(QFont("Consolas", 11, weight=QFont.Bold))
        grid.addWidget(self.lobby, 1, 1)

        self.IPandNames = QListWidget()
        self.IPandNames.setFixedWidth(300)
        self.IPandNames.setFont(QFont("Consolas", 11, weight=QFont.Bold))
        grid.addWidget(self.IPandNames, 1, 2)

        l = QLabel("ESO Packets:")
        grid.addWidget(l, 0, 0)

        l2 = QLabel("Players in lobby:")
        grid.addWidget(l2, 0, 1)

        l3 = QLabel("IP and ESO names database:")
        grid.addWidget(l3, 0, 2)

        self.groupBox = QGroupBox("Filter:")
        gridBox = QGridLayout()

        self.cb1 = QCheckBox("Show BLACK messages")
        self.cb1.setChecked(True)
        self.cb1.clicked.connect(self.filterClicked)
        gridBox.addWidget(self.cb1, 1, 0)

        self.cb2 = QCheckBox("Show VIOLET messages")
        self.cb2.setChecked(True)
        self.cb2.clicked.connect(self.filterClicked)
        gridBox.addWidget(self.cb2, 1, 1)

        self.cb3 = QCheckBox("Show BLUE messages")
        self.cb3.setChecked(True)
        self.cb3.clicked.connect(self.filterClicked)
        gridBox.addWidget(self.cb3, 1, 2)

        self.cb4 = QCheckBox("Show GREEN messages")
        self.cb4.setChecked(True)
        self.cb4.clicked.connect(self.filterClicked)
        gridBox.addWidget(self.cb4, 1, 3)

        self.cb5 = QCheckBox("Show RED messages")
        self.cb5.setChecked(True)
        self.cb5.clicked.connect(self.filterClicked)
        gridBox.addWidget(self.cb5, 1, 4)

        self.filter = QLineEdit(self)
        self.filter.textChanged.connect(self.filterClicked)
        gridBox.addWidget(self.filter, 0, 0, 1, 5)

        self.groupBox.setLayout(gridBox)
        grid.addWidget(self.groupBox, 2, 0)

        self.groupBox2 = QGroupBox("Filter:")
        gridBox2 = QGridLayout()

        self.filterIP = QLineEdit(self)
        self.filterIP.setFixedWidth(300)
        self.filterIP.textChanged.connect(self.filterIPandNames)
        gridBox2.addWidget(self.filterIP, 0, 0)

        self.groupBox2.setLayout(gridBox2)
        grid.addWidget(self.groupBox2, 2, 2)

        self.timer = QTimer()
        self.timer.timeout.connect(self.UpdateLobby)
        self.timer.setSingleShot(False)
        self.timer.start(500)

        self.jsonPackets = self.openJSONPackets("log.json")
        self.jsonIPandNames = self.openJSONIPandNames("IPandNames.json")

        self.thread = SniffThread()
        self.thread.DataToUpdate.connect(self.AddNewItemToPacketListBox)
        self.thread.activeIP.connect(self.LaunchPing)
        self.thread.IPandESO.connect(self.AddNewItemToIPandNamesListBox)
        self.thread.start()

        self.setFixedSize(1300, 480)
        self.setWindowTitle("ESO Packet Tracker")
        self.center()
        self.setWindowIcon(QIcon(self.getIconPath()))
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def filterClicked(self):
        for row in range(self.w.count()):
            a = self.w.item(row)
            filterMatching = (
                self.filter.text and self.filter.text().lower() in a.text().lower()
            )
            if self.w.item(row).foreground().color() == QColor(clBlack):
                a.setHidden(not (self.cb1.isChecked() and filterMatching))
            if self.w.item(row).foreground().color() == QColor(clViolet):
                a.setHidden(not (self.cb2.isChecked() and filterMatching))
            if self.w.item(row).foreground().color() == QColor(clBlue):
                a.setHidden(not (self.cb3.isChecked() and filterMatching))
            if self.w.item(row).foreground().color() == QColor(clGreen):
                a.setHidden(not (self.cb4.isChecked() and filterMatching))
            if self.w.item(row).foreground().color() == QColor(clRed):
                a.setHidden(not (self.cb5.isChecked() and filterMatching))
        self.w.scrollToBottom()

    def filterIPandNames(self):
        for row in range(self.IPandNames.count()):
            a = self.IPandNames.item(row)
            filterMatching = (
                self.filterIP.text and self.filterIP.text().lower() in a.text().lower()
            )
            a.setHidden(not filterMatching)

        self.IPandNames.scrollToBottom()

    def AddNewItemToPacketListBox(self, data):
        self.jsonPackets.append({"text": data[0], "color": data[1]})
        widgitItem = QListWidgetItem(data[0])
        widgitItem.setFont(QFont("Consolas", 11, weight=QFont.Bold))
        widgitItem.setForeground(QColor(data[1]))
        self.w.addItem(widgitItem)
        self.filterClicked()
        self.w.scrollToBottom()

    def AddNewItemToIPandNamesListBox(self, data):
        Item = next(
            (
                item
                for item in self.jsonIPandNames
                if item["IP"] == data["IP"] and item["ESO"] == data["ESO"]
            ),
            False,
        )
        if Item == False:
            self.jsonIPandNames.append({"IP": data["IP"], "ESO": data["ESO"]})
            widgitItem = QListWidgetItem(data["IP"] + " : " + data["ESO"])
            self.IPandNames.addItem(widgitItem)
            self.filterIPandNames()
            self.IPandNames.scrollToBottom()

    def UpdateIP(self, data):

        Item = next(
            (item for item in self.IPinLobby if item["IP"] == data["IP"]), False
        )
        if Item != False:
            Item["RTT"] = data["RTT"]
            # print(data["RTT"])

    def LaunchPing(self, data):

        Item = next((item for item in self.IPinLobby if item["IP"] == data), False)
        if Item == False:
            self.IPinLobby.append(
                {
                    "IP": data,
                    "LastUpdate": datetime.now(),
                    "RTT": "N/A",
                    "nicknames": [],
                }
            )

            thread = pingIP(data)
            thread.signals.playerinLobby.connect(self.UpdateIP)
            self.pool.start(thread)

        else:
            Item["LastUpdate"] = datetime.now()

    def UpdateLobby(self):
        self.IPinLobby = [
            IP
            for IP in self.IPinLobby
            if (datetime.now() - IP["LastUpdate"]).total_seconds() < 5
        ]
        widgetItems = []
        for i in self.IPinLobby:
            widgetItems.append(i["IP"] + " : " + i["RTT"])
        self.lobby.clear()
        self.lobby.addItems(widgetItems)

    # Сохранение JSON в файл
    def closeEvent(self, event):
        with open("log.json", "w+", encoding="utf-8") as f:
            json.dump(self.jsonPackets, f, ensure_ascii=False, sort_keys=True)
        with open("IPandNames.json", "w+", encoding="utf-8") as f:
            json.dump(self.jsonIPandNames, f, ensure_ascii=False, sort_keys=True)

    # Открытие JSON из файла
    def openJSONPackets(self, Path):
        with open(Path, "a+", encoding="utf-8") as data_file:
            data_file.seek(0)
            data = data_file.read()
            if data:
                j = json.loads(data)
                widgetItems = []
                for item in j:
                    widgetItems.append(item["text"])
                self.w.addItems(widgetItems)
                for i in range(self.w.count()):
                    item = self.w.item(i)
                    item.setForeground(QColor(j[i]["color"]))
                self.w.scrollToBottom()
                return j
            else:
                return []

        # Открытие JSON из файла

    def openJSONIPandNames(self, Path):
        with open(Path, "a+", encoding="utf-8") as data_file:
            data_file.seek(0)
            data = data_file.read()
            if data:
                j = json.loads(data)
                widgetItems = []
                for item in j:
                    widgetItems.append(item["IP"] + " : " + item["ESO"])
                self.IPandNames.addItems(widgetItems)
                return j
            else:
                return []


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())
