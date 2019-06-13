import ipaddress
import locale
import os
import socket
import struct

import xml.etree.ElementTree as ElementTree
from datetime import datetime, timezone

import requests
from dateutil.parser import parse
from PyQt5.QtCore import QThread, QThreadPool, pyqtSignal
from scapy.all import sniff
from scapy.layers.inet import IP, TCP, UDP

import localization
from Constants import clBlack, clBlue, clGreen, clRed, clViolet
from IPInfo import IPInfo

class SniffThread(QThread):
    DataToUpdate = pyqtSignal(tuple)
    activeIP = pyqtSignal(str)
    IPandESO = pyqtSignal(dict)
    speech = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.pool = QThreadPool()
        self.agecomIP = socket.gethostbyname("agecommunity.com")
        self.conagecomIP = socket.gethostbyname("connection.agecommunity.com")
        self.epIP = socket.gethostbyname("ep.eso-community.net")

    def utc_to_local(self, utc_dt):
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

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

    def ActionsAfterIP(self, data):
        self.DataToUpdate.emit(
            self.ColoredOutput(
                self.loc["playerconncet"].format(
                    n=data["Name"], IP=data["IP"], country=data["Country"]
                ),
                3,
            )
        )

        self.speech.emit(
            {
                "speechType": "connection",
                "text": self.loc["playerconnectvoice"].format(
                    n=data["Name"], country=data["Country"]
                ),
                "who": None,
            }
        )

    def SniffCallback(self, packet):

        if packet.haslayer(UDP):
            srcIP = packet[IP].src
            dstIP = packet[IP].dst
            data = bytes(packet[UDP].payload)
            try:
                # Ignore agecommunity.com and ep.eso-community.net

                if (
                    srcIP != self.agecomIP
                    and dstIP != self.agecomIP
                    and srcIP != self.conagecomIP
                    and dstIP != self.conagecomIP
                    and srcIP != self.epIP
                    and dstIP != self.epIP
                ):

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
                                self.speech.emit(
                                    {
                                        "speechType": "translateFromUDP",
                                        "text": text,
                                        "who": None,
                                    }
                                )

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

                                self.speech.emit(
                                    {
                                        "speechType": "taunts",
                                        "text": text[9:],
                                        "who": "",
                                    }
                                )                                

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

                                                        thread = IPInfo(
                                                            ip=str(pIP), name=n.text
                                                        )
                                                        thread.signals.infoSignal.connect(
                                                            self.ActionsAfterIP
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

                                        self.speech.emit(
                                            {
                                                "speechType": "translateFromTCP",
                                                "text": w.text,
                                                "who": self.loc[
                                                    "playerwhispervoice"
                                                ].format(n=n.text),
                                            }
                                        )

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

                                                    self.speech.emit(
                                                        {
                                                            "speechType": "friends",
                                                            "text": self.loc[
                                                                "friendonline"
                                                            ].format(n=n.text, gt=gt),
                                                            "who": None,
                                                        }
                                                    )

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
