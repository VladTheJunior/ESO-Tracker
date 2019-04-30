import ipaddress
import json
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

init(autoreset=True)

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
                                            + f"Player {un} left the chat {cn}"
                                        )
                                        return
                                    n = c.attrib["n"]
                                    printWithLog(
                                        Fore.CYAN
                                        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        + " : "
                                        + Fore.YELLOW
                                        + f'You left the chat "{n}"'
                                    )
                                    return

                                # Message to chat
                                if (ty == "event" or ty == "request") and tp == "msg":
                                    cn = c.attrib["n"]
                                    if ty == "event":
                                        u = c.find("./u")
                                        un = u.attrib["n"]
                                        m = u.find("./m")
                                        msg = (
                                            Fore.MAGENTA
                                            + f'{un} writes to chat "{cn}": {m.text}'
                                        )
                                    else:
                                        m = c.find("./m")
                                        msg = (
                                            Fore.YELLOW
                                            + f'You write to chat "{cn}": {m.text}'
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
                                        + "You updated the chat list."
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
                                            + f'Player {un} joined the chat "{cn}"'
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
                                        + f'You joined the chat "{n}"'
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
                                        + f'Player {un.text} invited you to the lobby "{n.text}": map {s10.text}, players({playerstr})'
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
                                        + f'Lobby "{n.text}" updated: map {s10.text}, players({playerstr})'
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
                                        + f"Player {n.text} was removed"
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
                                        + "You created a lobby"
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
                                        + "You left the lobby"
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
                                                country = IPinfo["country"]["name_en"]
                                            printWithLog(
                                                Fore.CYAN
                                                + datetime.now().strftime(
                                                    "%Y-%m-%d %H:%M:%S"
                                                )
                                                + " : "
                                                + Fore.GREEN
                                                + f"Player {n.text} is connecting: {IP}, {country}"
                                            )
                                            tts = gTTS(
                                                f"Player {n.text} from {country} is connecting",
                                                lang="en",
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
                                + f"You started QuickSeatch"
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
                                + f"You invited {iu.text} to the lobby"
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
                                + f"You canceled QuickSerach"
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
                                    + f"You removed player {name.text} from friends/foes list"
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
                                            + f"You added player {n.text} to friends list"
                                        )
                                    else:
                                        printWithLog(
                                            Fore.CYAN
                                            + datetime.now().strftime(
                                                "%Y-%m-%d %H:%M:%S"
                                            )
                                            + " : "
                                            + Fore.YELLOW
                                            + f"You added player {n.text} to foes list"
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
                                        + f"You moved player {name.text} to friends list"
                                    )
                                else:
                                    printWithLog(
                                        Fore.CYAN
                                        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        + " : "
                                        + Fore.YELLOW
                                        + f"You moved player {name.text} to foes list"
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
                                    + f"Player stat {un.text}\n"
                                    + f"Registration date: {cd.text}\n"
                                    + f"Last active: {lld.text}\n"
                                    + f"Clan {ca.text} - {cn.text}\n"
                                    + f"Supremacy: games {sg.text}, wins {sw.text}, winrate {sp.text}%, PR {spts.text} \n"
                                    + f"Treaty: games {tg.text}, wins {tw.text}, winrate {tp.text}%, PR {tpts.text} \n"
                                    + f"Deathmatch: games {dg.text}, wins {dw.text}, winrate {dp.text}%, PR {dpts.text} \n"
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
                                + f"Player {n.text} whispers : {w.text}"
                            )
                            tts = gTTS(f"Player {n.text} whispers", lang="en")
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
                                + f"You whisper to {name.text} : {whisper.text}"
                            )
                            return
                        # List of lobbies
                        if ty == "request" and tp == "list":
                            printWithLog(
                                Fore.CYAN
                                + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                + " : "
                                + Fore.YELLOW
                                + f"You updated list of lobbies"
                            )
                            return
                        # Population ESO
                        if ty == "event" and tp == "population":
                            printWithLog(
                                Fore.CYAN
                                + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                + " : "
                                + Fore.MAGENTA
                                + f"Players on ESO: {root.find('./numPlayers').text}"
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
                                    + f"QuickSearch updated: {ut.text}"
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
                                        + f"Friend {n.text} left ESO"
                                    )
                                    return
                                if m is not None and gid is not None:
                                    if gid.text == "1":
                                        gt = "Vanilla"
                                    else:
                                        gt = "The Asian Dynasties"
                                    if m.text == "IG":
                                        printWithLog(
                                            Fore.CYAN
                                            + datetime.now().strftime(
                                                "%Y-%m-%d %H:%M:%S"
                                            )
                                            + " : "
                                            + Fore.MAGENTA
                                            + f"Friend {n.text} started game in {gt}"
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
                                            + f"Friend {n.text} is online in {gt}"
                                        )
                                        tts = gTTS(
                                            f"Friend {n.text} is online in {gt}",
                                            lang="en",
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
