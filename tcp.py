import ipaddress
import json
import locale
import os
import os.path
import random
import string
import struct
import xml.etree.ElementTree as ElementTree
from datetime import datetime, timezone

import requests
from colorama import Fore, init
from dateutil.parser import parse
from gtts import gTTS
from playsound import playsound
from scapy.all import sniff
from scapy.layers.inet import TCP

import localization

init(autoreset=True)
lang = list(locale.getdefaultlocale())[0][0:2]

if lang == "ru":
    loc = localization.ru
else:
    loc = localization.en

if not os.path.exists("TTS"):
    os.makedirs("TTS")


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def printWithLog(msg):
    print(msg)
    print(msg, file=f)
    f.flush()


def bordered(text):
    lines = text
    width = max(len(s) for s in lines)
    res = ["┌" + "─" * width + "┐"]
    for s in lines:
        res.append("│" + (s + " " * width)[:width] + "│")
    res.append("└" + "─" * width + "┘")
    return "\n".join(res)


def getJSON(URL, params=None):
    r = requests.get(URL, params=params, timeout=10)
    return r.json()


def getXML(URL, params):
    r = requests.get(URL, params=params, timeout=10)
    return ElementTree.fromstring(r.text)


def play_sound(sound):
    playsound(os.path.join("TTS", sound + ".mp3"), False)


def pkt_callback(packet):
    if packet[TCP].payload is not None:
        data = packet[TCP].payload
        try:
            start = bytes(data).find(b"\x3c\x65\x73\x6f")
            if start != -1:
                end = bytes(data).find(b"\x3c\x2f\x65\x73\x6f\x3e", start)
                if end != -1:
                    if -(len(bytes(data)) - end - 6) != 0:
                        xml = str(
                            bytes(data)[start : -(len(bytes(data)) - end - 6)].decode(
                                "UTF-8"
                            )
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
                                    ty == "response" or ty == "request" or ty == "event"
                                ) and tp == "leave":
                                    # Ignore request
                                    if ty == "request":
                                        return
                                    # Leave event
                                    if ty == "event":
                                        u = c.find("./u")
                                        cn = c.attrib["n"]
                                        un = u.attrib["n"]
                                        printWithLog(
                                            Fore.CYAN
                                            + datetime.now().strftime(
                                                "%Y-%m-%d %H:%M:%S"
                                            )
                                            + " : "
                                            + Fore.MAGENTA
                                            + loc["playerleftchat"].format(un=un, cn=cn)
                                        )
                                        return
                                    n = c.attrib["n"]
                                    printWithLog(
                                        Fore.CYAN
                                        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        + " : "
                                        + Fore.YELLOW
                                        + loc["youleftchat"].format(n=n)
                                    )
                                    return

                                # Message to chat
                                if (ty == "event" or ty == "request") and tp == "msg":
                                    cn = c.attrib["n"]
                                    if ty == "event":
                                        u = c.find("./u")
                                        un = u.attrib["n"]
                                        m = u.find("./m")
                                        msg = Fore.MAGENTA + loc[
                                            "playerwritechat"
                                        ].format(un=un, cn=cn, m=m.text)
                                    else:
                                        m = c.find("./m")
                                        msg = Fore.YELLOW + loc["youwritechat"].format(
                                            cn=cn, m=m.text
                                        )
                                    printWithLog(
                                        Fore.CYAN
                                        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        + " : "
                                        + msg
                                    )
                                    return
                                # Enter to chat browser
                                if ty == "response" and tp == "list":
                                    printWithLog(
                                        Fore.CYAN
                                        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        + " : "
                                        + Fore.YELLOW
                                        + loc["updatedchatlist"]
                                    )
                                    return
                                # Join to chat
                                if (
                                    ty == "response" or ty == "request" or ty == "event"
                                ) and tp == "join":
                                    # Ignore request
                                    if ty == "request":
                                        return
                                    # Event join
                                    if ty == "event":
                                        u = c.find("./u")
                                        cn = c.attrib["n"]
                                        un = u.attrib["n"]
                                        printWithLog(
                                            Fore.CYAN
                                            + datetime.now().strftime(
                                                "%Y-%m-%d %H:%M:%S"
                                            )
                                            + " : "
                                            + Fore.MAGENTA
                                            + loc["playerjoinchat"].format(un=un, cn=cn)
                                        )
                                        return
                                    n = c.attrib["n"]
                                    messages = []
                                    for item in c.findall("h"):
                                        t = item.find("./t")
                                        f = item.find("./f")
                                        m = item.find("./m")
                                        messages.append(
                                            Fore.MAGENTA
                                            + f.text
                                            + " ["
                                            + utc_to_local(parse(t.text)).strftime(
                                                "%d.%m.%y %H:%M:%S"
                                            )
                                            + "] : "
                                            + m.text
                                        )
                                    printWithLog(
                                        Fore.CYAN
                                        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        + " : "
                                        + Fore.YELLOW
                                        + loc["youjoinchat"].format(n=n)
                                        + "\n"
                                        + "\n".join(messages)
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
                                        (i, "s" + str(start + 24 * i)) for i in range(8)
                                    ]:
                                        if st.find("./" + pstr) is not None:
                                            players.append(st.find("./" + pstr).text)
                                    playerstr = ", ".join(players)
                                    printWithLog(
                                        Fore.CYAN
                                        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        + " : "
                                        + Fore.YELLOW
                                        + loc["playerinvite"].format(
                                            un=un.text,
                                            n=n.text,
                                            s10=s10.text,
                                            playerstr=playerstr,
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
                                        (i, "s" + str(start + 24 * i)) for i in range(8)
                                    ]:
                                        if st.find("./" + pstr) is not None:
                                            players.append(st.find("./" + pstr).text)
                                    playerstr = ", ".join(players)
                                    printWithLog(
                                        Fore.CYAN
                                        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        + " : "
                                        + Fore.YELLOW
                                        + loc["lobbyupdated"].format(
                                            n=n.text, s10=s10.text, playerstr=playerstr
                                        )
                                    )
                                    return
                                # Remove user
                                if ty == "event" and tp == "removeuser":
                                    u = g.find("./u")
                                    n = u.find("./n")
                                    printWithLog(
                                        Fore.CYAN
                                        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        + " : "
                                        + Fore.YELLOW
                                        + loc["playerremoved"].format(n=n.text)
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
                                    printWithLog(
                                        Fore.CYAN
                                        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        + " : "
                                        + Fore.YELLOW
                                        + loc["createlobby"]
                                    )
                                    return
                                # Remove/ leave/ cancel
                                if (ty == "request" or ty == "response") and (
                                    tp == "remove" or tp == "leave" or tp == "cancel"
                                ):
                                    if ty == "response":
                                        return
                                    printWithLog(
                                        Fore.CYAN
                                        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        + " : "
                                        + Fore.YELLOW
                                        + loc["youleftlobby"]
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
                                        if xip is not None and n is not None:
                                            IP = ipaddress.IPv4Address(
                                                struct.pack("<L", int(xip.text, 16))
                                            )
                                            IPinfo = getJSON(
                                                "http://api.sypexgeo.net/json/"
                                                + str(IP)
                                            )
                                            if IPinfo["country"] is None:
                                                country = ""
                                            else:
                                                country = IPinfo["country"][loc["country"]]
                                            printWithLog(
                                                Fore.CYAN
                                                + datetime.now().strftime(
                                                    "%Y-%m-%d %H:%M:%S"
                                                )
                                                + " : "
                                                + Fore.GREEN
                                                + loc["playerconncet"].format(
                                                    n=n.text, IP=IP, country=country
                                                )
                                            )
                                            tts = gTTS(
                                                loc["playerconnectvoice"].format(
                                                    n=n.text, country=country
                                                ),
                                                lang=loc["language"],
                                            )
                                            sound = "".join(
                                                random.choices(
                                                    string.ascii_uppercase
                                                    + string.digits,
                                                    k=32,
                                                )
                                            )
                                            tts.save(
                                                os.path.join("TTS", sound + ".mp3")
                                            )
                                            play_sound(sound)
                                            return
                        # Start QuickSearch
                        if (ty == "response" or ty == "request") and tp == "begin":
                            # Ignore request
                            if ty == "request":
                                return
                            printWithLog(
                                Fore.CYAN
                                + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                + " : "
                                + Fore.YELLOW
                                + loc["startqs"]
                            )
                            return
                        # Send invite
                        if (ty == "response" or ty == "request") and tp == "invite":
                            # Ignore response
                            if ty == "response":
                                return
                            iu = root.find("./iu")
                            printWithLog(
                                Fore.CYAN
                                + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                + " : "
                                + Fore.YELLOW
                                + loc["youinvite"].format(iu=iu.text)
                            )
                            return
                        # Cancel QuickSearch
                        if (ty == "response" or ty == "request") and tp == "cancel":
                            # Ignore request
                            if ty == "request":
                                return
                            printWithLog(
                                Fore.CYAN
                                + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                + " : "
                                + Fore.YELLOW
                                + loc["cancelqs"]
                            )
                            return
                        # Remove player from list
                        if (ty == "response" or ty == "request") and tp == "remove":
                            # Ignore request
                            if ty == "request":
                                return
                            user = root.find("user")
                            if user is not None:
                                name = user.find("name")
                                printWithLog(
                                    Fore.CYAN
                                    + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    + " : "
                                    + Fore.YELLOW
                                    + loc["fflremove"].format(name=name.text)
                                )
                                return
                        # Add player to list
                        if (ty == "response" or ty == "request") and tp == "add":
                            # Ignore request
                            if ty == "request":
                                return
                            user = root.find("user")
                            if user is not None:
                                n = user.find("n")
                                if n is not None:
                                    b = user.attrib["b"]
                                    if b == "0":
                                        printWithLog(
                                            Fore.CYAN
                                            + datetime.now().strftime(
                                                "%Y-%m-%d %H:%M:%S"
                                            )
                                            + " : "
                                            + Fore.YELLOW
                                            + loc["fradded"].format(n=n.text)
                                        )
                                    else:
                                        printWithLog(
                                            Fore.CYAN
                                            + datetime.now().strftime(
                                                "%Y-%m-%d %H:%M:%S"
                                            )
                                            + " : "
                                            + Fore.YELLOW
                                            + loc["fadded"].format(n=n.text)
                                        )
                                    return
                        # Update list
                        if (ty == "response" or ty == "request") and tp == "update":
                            # Ignore request
                            if ty == "request":
                                return
                            user = root.find("user")
                            if user is not None:
                                name = user.find("name")
                                blocked = user.attrib["blocked"]
                                if blocked == "0":
                                    printWithLog(
                                        Fore.CYAN
                                        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        + " : "
                                        + Fore.YELLOW
                                        + loc["frmoved"].format(name=name.text)
                                    )
                                else:
                                    printWithLog(
                                        Fore.CYAN
                                        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        + " : "
                                        + Fore.YELLOW
                                        + loc["fmoved"].format(name=name.text)
                                    )
                                return
                        # Player stat
                        if ty == "request" and tp == "metaquery":
                            return
                        if (ty == "response" or ty == "request") and tp == "query":
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
                                printWithLog(
                                    Fore.CYAN
                                    + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    + " : "
                                    + Fore.MAGENTA
                                    + loc["stat"].format(un=un.text)
                                    + loc["regdate"].format(cd=cd.text)
                                    + loc["lastactive"].format(lld=lld.text)
                                    + loc["clan"].format(ca=ca.text, cn=cn.text)
                                    + loc["supremacy"].format(
                                        sg=sg.text,
                                        sw=sw.text,
                                        sp=sp.text,
                                        spts=spts.text,
                                    )
                                    + loc["treaty"].format(
                                        tg=tg.text,
                                        tw=tw.text,
                                        tp=tp.text,
                                        tpts=tpts.text,
                                    )
                                    + loc["dm"].format(
                                        dg=dg.text,
                                        dw=dw.text,
                                        dp=dp.text,
                                        dpts=dpts.text,
                                    )
                                )
                                return
                        # Whisper to us
                        if ty == "event" and tp == "whisper":
                            user = root.find("./user")
                            n = user.find("./n")
                            w = user.find("./w")
                            printWithLog(
                                Fore.CYAN
                                + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                + " : "
                                + Fore.GREEN
                                + loc["playerwhisper"].format(n=n.text, w=w.text)
                            )
                            tts = gTTS(
                                loc["playerwhispervoice"].format(n=n.text),
                                lang=loc["language"],
                            )
                            sound = "".join(
                                random.choices(
                                    string.ascii_uppercase + string.digits, k=32
                                )
                            )
                            tts.save(os.path.join("TTS", sound + ".mp3"))
                            play_sound(sound)
                            return

                        # we whisper
                        if (ty == "request" or ty == "response") and tp == "whisper":
                            if ty == "response":
                                return
                            user = root.find("./user")
                            name = user.find("./name")
                            whisper = user.find("./whisper")
                            printWithLog(
                                Fore.CYAN
                                + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                + " : "
                                + Fore.YELLOW
                                + loc["youwhisper"].format(
                                    name=name.text, whisper=whisper.text
                                )
                            )
                            return
                        # List of lobbies
                        if ty == "request" and tp == "list":
                            printWithLog(
                                Fore.CYAN
                                + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                + " : "
                                + Fore.YELLOW
                                + loc["listlobbyupdate"]
                            )
                            return
                        # Population ESO
                        if ty == "event" and tp == "population":
                            printWithLog(
                                Fore.CYAN
                                + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                + " : "
                                + Fore.MAGENTA
                                + loc["eso"].format(num=root.find("./numPlayers").text)
                            )
                            return

                        if ty == "event" and tp == "update":
                            user = root.find("./user")
                            pn = root.find("./pn")
                            if pn is not None:
                                ut = root.find("./ut")
                                printWithLog(
                                    Fore.CYAN
                                    + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    + " : "
                                    + Fore.MAGENTA
                                    + loc["qsupdated"].format(ut=ut.text)
                                )
                                return
                            # Friends
                            if user is not None:
                                n = user.find("./n")
                                s = user.find("./s")
                                m = user.find("./m")
                                gid = user.find("./gid")
                                if s.text == "offline":
                                    printWithLog(
                                        Fore.CYAN
                                        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        + " : "
                                        + Fore.MAGENTA
                                        + loc["friendleft"].format(n=n.text)
                                    )
                                    return
                                if m is not None and gid is not None:
                                    if gid.text == "1":
                                        gt = loc["Vanilla"]
                                    else:
                                        gt = loc["tad"]
                                    if m.text == "IG":
                                        printWithLog(
                                            Fore.CYAN
                                            + datetime.now().strftime(
                                                "%Y-%m-%d %H:%M:%S"
                                            )
                                            + " : "
                                            + Fore.MAGENTA
                                            + loc["friendingame"].format(
                                                n=n.text, gt=gt
                                            )
                                        )
                                        return
                                    else:
                                        printWithLog(
                                            Fore.CYAN
                                            + datetime.now().strftime(
                                                "%Y-%m-%d %H:%M:%S"
                                            )
                                            + " : "
                                            + Fore.GREEN
                                            + loc["friendonline"].format(
                                                n=n.text, gt=gt
                                            )
                                        )
                                        tts = gTTS(
                                            loc["friendonline"].format(n=n.text, gt=gt),
                                            lang=loc["language"],
                                        )
                                        sound = "".join(
                                            random.choices(
                                                string.ascii_uppercase + string.digits,
                                                k=32,
                                            )
                                        )
                                        tts.save(os.path.join("TTS", sound + ".mp3"))
                                        play_sound(sound)

                                        return
                                else:
                                    return
                    printWithLog(
                        Fore.CYAN
                        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        + " : "
                        + Fore.WHITE
                        + xml
                    )
        except Exception as e:
            printWithLog(
                Fore.CYAN
                + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                + " : "
                + Fore.RED
                + str(e)
                + "\n"
                + str(data)
            )


if __name__ == "__main__":
    f = open("log.txt", "a+", encoding="utf-8")
    f.seek(0)
    print(f.read())
    print(
        Fore.GREEN
        + bordered(
            [
                "TCP Tracker for Age of Empires III",
                "Version 2019.04.30",
                "Copyright (c) 2019 XaKO",
                "Ready!",
            ]
        )
        + "\n"
    )
    sniff(prn=pkt_callback, filter="tcp port 2300", store=0)
