import zlib
import re
import struct
import os
import sys
from datetime import datetime
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal
import json


class RecordParser:
    def __init__(self):
        self.Data = bytes()
        self.Offset = 0
        self.Game = {}
        self.Players = {}
        self.CivsTAD = {}
        self.CivsVanilla = {}
        self.CivsTWC = {}
        self.TechsTAD = {}
        self.TechsVanilla = {}
        self.TechsTWC = {}
        self.UnitsTAD = {}
        self.UnitsVanilla = {}
        self.UnitsTWC = {}
        with open(os.path.join("Data", "CivsTAD.json"), "r", encoding="utf-8") as data_file:
            data_file.seek(0)
            data = data_file.read()
            if data:
                self.CivsTAD = json.loads(data)
        with open(os.path.join("Data", "CivsVanilla.json"), "r", encoding="utf-8") as data_file:
            data_file.seek(0)
            data = data_file.read()
            if data:
                self.CivsVanilla = json.loads(data)
        with open(os.path.join("Data", "CivsTWC.json"), "r", encoding="utf-8") as data_file:
            data_file.seek(0)
            data = data_file.read()
            if data:
                self.CivsTWC = json.loads(data)
        with open(os.path.join("Data", "TechsTWC.json"), "r", encoding="utf-8") as data_file:
            data_file.seek(0)
            data = data_file.read()
            if data:
                self.TechsTWC = json.loads(data)
        with open(os.path.join("Data", "UnitsTWC.json"), "r", encoding="utf-8") as data_file:
            data_file.seek(0)
            data = data_file.read()
            if data:
                self.UnitsTWC = json.loads(data)
        with open(os.path.join("Data", "UnitsTAD.json"), "r", encoding="utf-8") as data_file:
            data_file.seek(0)
            data = data_file.read()
            if data:
                self.UnitsTAD = json.loads(data)
        with open(os.path.join("Data", "TechsTAD.json"), "r", encoding="utf-8") as data_file:
            data_file.seek(0)
            data = data_file.read()
            if data:
                self.TechsTAD = json.loads(data)
        with open(os.path.join("Data", "TechsVanilla.json"), "r", encoding="utf-8") as data_file:
            data_file.seek(0)
            data = data_file.read()
            if data:
                self.TechsVanilla = json.loads(data)
        with open(os.path.join("Data", "UnitsVanilla.json"), "r", encoding="utf-8") as data_file:
            data_file.seek(0)
            data = data_file.read()
            if data:
                self.UnitsVanilla = json.loads(data)

    def getCivNameById(self, id):
        if id == 1:
            return "Spanish"
        elif id == 2:
            return "British"
        elif id == 3:
            return "French"
        elif id == 4:
            return "Portuguese"
        elif id == 5:
            return "Dutch"
        elif id == 6:
            return "Russians"
        elif id == 7:
            return "Germans"
        elif id == 8:
            return "Ottomans"
        elif id == 15:
            return "XPIroquois"
        elif id == 16:
            return "XPSioux"
        elif id == 17:
            return "XPAztec"
        elif id == 19:
            return "Japanese"
        elif id == 20:
            return "Chinese"
        elif id == 21:
            return "Indians"
        else:
            return ""


    def Parser(self, filePath):
        try:
            f = open(filePath, "rb")
            if f.read(4) != b"l33t":
                raise Exception("Not a AoE3 compressed file")
            f.seek(6, 1)
            self.Data = f.read()
            self.Data = zlib.decompress(self.Data, wbits=-zlib.MAX_WBITS)
            if self.Data[0] != 3:
                raise Exception("Not a AoE3 recorded game")
            self.Data = self.Data[17:]
            if self.Data[0] != 1:
                raise Exception("Not a multiplayer game")
            self.SkipBytes(13)
            #print(self.Data[self.Offset - 12:self.Offset+12])
            self.Game["view_point"] = self.ReadInt8()
            self.SkipBytes(236)
            self.ReadExeInfo()
            self.SkipBytes(8)
            self.SkipString()
            # Alternative map name? Usually null except for Mutation Invasion scenario
            if self.Game["exe_version"] == "5.0106.1031.0428":
                self.SkipBytes(26)
            else:
                self.SkipBytes(30)
            self.ReadGameInfo()
            self.ReadCustomInfo()
            self.ReadPlayersTeams()
            self.ReadPlayersDecks()
            self.ReadPlayersActions()
        finally:
            f.close()

    def SkipString(self):
        length = self.ReadInt32()
        self.Offset += length * 2

    def SkipBytes(self, length):
        self.Offset += length

    def CurrentOffset(self):
        return self.Offset

    def ReadData(self, Format, length):
        data = self.Data[self.Offset: self.Offset + length]
        self.Offset += length
        result = struct.unpack(Format, data)
        return result[0]

    def ReadExeInfo(self):
        data = self.ReadString()
        matches = re.search("^(.*?) (\\d+\\.\\d+\\.\\d+\\.\\d+)", data)
        self.Game["exe_name"] = matches[1]
        self.Game["exe_version"] = matches[2]

    def ReadCustomInfo(self):
        self.Game["duration"] = 0
        self.Game["ep_version"] = None
        self.Game["played_date"] = None
        self.Game["is_observer_ui"] = int(
            self.Search("_FeatureLoader") and self.Search("_ConstantLoader")
        )
        self.Game["have_observer_ui"] = int(
            self.Game["is_observer_ui"] and self.Search("recordGameViewLock")
        )
        needle = "ESOC Patch "
        if self.Search(needle, False, True):
            epVersion = self.Data[self.Offset: self.Offset + 16]
            matches = re.search(
                "(\\d).(\\d)\\.?(\\d).(\\d)", epVersion.decode("utf-16le")
            )
            if matches:
                self.Game["ep_version"] = int(
                    f"{matches[1]}{matches[2]}{matches[3]}{matches[4]}"
                )
                if self.Game["ep_version"] >= 5110:
                    needle = "Played on: "
                    if self.Search(needle, False, True):
                        self.Game["played_date"] = self.Data[
                            self.CurrentOffset(): self.CurrentOffset() + 38
                        ].decode("utf-16le")
            else:
                raise Exception(f"Unknown EP version: {epVersion}")
        if self.Game["exe_version"][0] == "4":
            self.Game["expansion"] = 0
        elif self.Game["exe_version"][0] == "5":
            self.Game["expansion"] = 1
        elif self.Game["exe_version"][0] == "6":
            self.Game["expansion"] = 2

    def ReadPlayersTeams(self):
        playersWithoutTeam = self.Game["numplayers"]
        self.ResetOffset()
        while playersWithoutTeam > 0 and self.Search(b"\x54\x45", True, True, False):
            self.SkipInt32()
            key = self.ReadInt32()
            if (
                    (self.Game["expansion"] == 0 and key == 8)
                    or (self.Game["expansion"] == 1 and key == 9)
                    or (self.Game["expansion"] == 2 and key == 12)
            ):
                teamId = self.ReadInt32()
                teamName = self.ReadString()
                for _ in range(0, self.ReadInt32()):
                    playerId = str(self.ReadInt32())
                    if playerId in self.Players:
                        playersWithoutTeam -= 1
                        self.Players[playerId]["teamid"] = teamId
                        self.Players[playerId]["teamname"] = teamName
        if playersWithoutTeam > 0:
            raise Exception("Couldnt find all players teams")

    def ReadGameInfo(self):
        while True:

            name = self.ReadString()
            Type = self.ReadInt32()
            if Type == 1:
                value = self.ReadFloat()
            elif Type == 2:
                value = self.ReadInt32()
            elif Type == 5:
                value = self.ReadInt8()
            elif Type == 9:
                value = self.ReadString()
            matches = re.search("^game(.*)", name)
            if matches:

                matches2 = re.search("^player(\\d+)(.*)", matches[1])
                if matches2:
                    if int(matches2[1]) > 0:
                        if int(matches2[1]) > self.Game["numplayers"]:
                            break
                        if not matches2[1] in self.Players:
                            self.Players[matches2[1]] = {"actions": [], "decks": [
                            ], "is_resigned": 0, "selectedDeckId": -1}
                        self.Players[matches2[1]][matches2[2]] = value
                else:
                    self.Game[matches[1]] = value
            else:
                self.Game[name] = value

    def ReadPlayersDecks(self):
        self.ResetOffset()
        currentPlayerId = 1
        while self.Search(b"\x44\x6b", True, False, False):
            decks = []
            currentDeckId = 1
            self.SkipBytes(-4)
            while True:
                decksCount = self.ReadInt32()
                if decksCount == 0:
                    if self.ReadInt32() == 0:
                        break
                    else:
                        decksCount = 1
                        self.SkipBytes(-4)
                leaveLoop = False
                for _ in range(0, decksCount):
                    if self.ReadInt8() != b"D" or self.ReadInt8() != b"k":
                        leaveLoop = True
                        break
                    nextDeckOffset = self.ReadInt32()
                    nextDeckOffset += self.CurrentOffset()
                    if self.ReadInt32() != 4:
                        leaveLoop = True
                        break
                    deckId = self.ReadInt32()
                    deckName = self.ReadString()
                    gameId = self.ReadInt32()  # 1 = Vanilla, 2 = TWC, 4 = TAD
                    isDefault = self.ReadInt8()
                    techsIds = []
                    for _ in range(0, self.ReadInt32()):
                        techsIds.append(self.ReadInt32())

                    decks.append({
                        "currentDeckId": currentDeckId,
                        "id": deckId,
                        "name": deckName,
                        "game_id": gameId,
                        "is_default": isDefault,
                        "cards": techsIds,

                    })

                    self.GoToOffset(nextDeckOffset)
                if leaveLoop:
                    break
                currentDeckId += 1
            have_deck = False
            for deck in decks:
                # 	Index	Info.
                # 	1		Player decks available in this game, can have vanilla and TWC decks if expansion is TAD
                # 	2		Decks definied in the homecity files (Static Deck and My Deck on RE/EP)
                # 	3		Revolution deck definied in the homecity files
                # 	3/4		Player decks NOT available in this game, i.e: you have TAD decks but are playing Vanilla
                if deck["currentDeckId"] == 1:
                    if self.getCivNameById(self.Players[str(currentPlayerId)]["civ"]) != "":
                        if self.Game["expansion"] == 2:
                            CurCiv = self.CivsTAD[self.getCivNameById(
                                self.Players[str(currentPlayerId)]["civ"])]
                        elif self.Game["expansion"] == 1:
                            CurCiv = self.CivsTWC[self.getCivNameById(
                                self.Players[str(currentPlayerId)]["civ"])]
                        else:
                            CurCiv = self.CivsVanilla[self.getCivNameById(
                                self.Players[str(currentPlayerId)]["civ"])]

                        techs = [CurCiv[str(card)] if str(card) in CurCiv else {"name": "UNKNOWN " + str(card), "age": "4",
                                                                                "DisplayName": {"en": None, "ru": None}, "Icon": None, "RolloverText": {"en": None, "ru": None}} for card in deck["cards"]]
                        sortded_techs = []
                        for card in CurCiv.values():
                            for tech in techs:
                                if card["name"] == tech["name"]:
                                    sortded_techs.append(tech)
                                    break

                        sortded_techs = sorted(
                            sortded_techs, key=lambda c: int(c["age"]))
                        deck["cards"] = sortded_techs

                        self.Players[str(currentPlayerId)
                                     ]["decks"].append(deck)
                        have_deck = True
                    else:
                        self.Players[str(currentPlayerId)
                                     ]["decks"].append(deck)
            if have_deck:
                currentPlayerId += 1

    def ReadPlayersActions(self):
        if not self.Search(b"\x9a\x99\x99\x3d", False, False, False):
            raise Exception("Couldnt find players actions")
        self.SkipBytes(130)
        self.Game["duration"] += ord(self.ReadInt8())

        selectedCount = self.ReadInt8()

        if selectedCount != b"\x00":
            selectedIds = []
            for _ in range(0, selectedCount):
                selectedIds.append(self.ReadInt32())
            self.ExpectedInt8(0)
            action = {"pid": str(ord(self.Game["view_point"])), "duration": self.Game["duration"], "type": "selected", "ids": selectedIds}
            #if action not in self.Players[str(ord(self.Game["view_point"]))]["actions"]:
            #    self.Players[str(ord(self.Game["view_point"]))]["actions"].append(action)
        else:
            if not self.Search(
                    b"\x01\x00\x00\x00\x00\x00\x00\x00\x00\x19", True, False, False
            ):
                raise Exception("Couldnt find players actions")

        while True:

            self.SkipBytes(113)

            try:
                mainCommand = ord(self.ReadInt8())

            except:

                break
            if mainCommand == 0:
                break
            hasCommands = True
            selectObjects = False
            if mainCommand == 33 or mainCommand == 65:
                pass
            elif mainCommand == 1:
                hasCommands = False
            elif mainCommand == 161 or mainCommand == 193:
                selectObjects = True
            elif mainCommand == 129:
                hasCommands = False
                selectObjects = True
            elif (
                    mainCommand == 35
                    or mainCommand == 37
                    or mainCommand == 41
                    or mainCommand == 67
                    or mainCommand == 73
            ):
                self.SkipBytes(4)
            elif mainCommand == 3 or mainCommand == 5 or mainCommand == 9:
                self.SkipBytes(4)
                hasCommands = False
            elif (
                    mainCommand == 163
                    or mainCommand == 165
                    or mainCommand == 169
                    or mainCommand == 195
                    or mainCommand == 201
            ):
                self.SkipBytes(4)
                selectObjects = True
            elif mainCommand == 131 or mainCommand == 133 or mainCommand == 137:
                self.SkipBytes(4)
                hasCommands = False
                selectObjects = True
            elif (
                    mainCommand == 39
                    or mainCommand == 43
                    or mainCommand == 45
                    or mainCommand == 75
            ):
                self.SkipBytes(8)
            # 11 Camera movement?
            elif mainCommand == 7 or mainCommand == 11 or mainCommand == 13:
                self.SkipBytes(8)
                hasCommands = False
            elif (
                    mainCommand == 167
                    or mainCommand == 171
                    or mainCommand == 173
                    or mainCommand == 203
            ):
                self.SkipBytes(8)
                selectObjects = True
            elif mainCommand == 135 or mainCommand == 139 or mainCommand == 141:
                self.SkipBytes(8)
                hasCommands = False
                selectObjects = True
            elif mainCommand == 47:
                self.SkipBytes(12)
            # // Zoom-in/out
            elif mainCommand == 15:
                self.SkipBytes(12)
                hasCommands = False
            elif mainCommand == 175 or mainCommand == 207:
                self.SkipBytes(12)
                selectObjects = True
            elif mainCommand == 143:
                self.SkipBytes(12)
                hasCommands = False
                selectObjects = True
            elif mainCommand == 17:
                self.SkipBytes(36)
                hasCommands = False
            elif mainCommand == 177:
                self.SkipBytes(36)
                selectObjects = True
            elif mainCommand == 145:
                self.SkipBytes(36)
                hasCommands = False
                selectObjects = True
            elif mainCommand == 19 or mainCommand == 21 or mainCommand == 25:
                self.SkipBytes(40)
                hasCommands = False
            elif mainCommand == 55 or mainCommand == 59:
                self.SkipBytes(44)
            elif mainCommand == 23 or mainCommand == 27 or mainCommand == 29:
                self.SkipBytes(44)
                hasCommands = False
            elif mainCommand == 187:
                self.SkipBytes(44)
                selectObjects = True
            elif mainCommand == 155:
                self.SkipBytes(44)
                hasCommands = False
                selectObjects = True
            elif mainCommand == 63:
                self.SkipBytes(48)
            elif mainCommand == 31:
                self.SkipBytes(48)
                hasCommands = False
            elif mainCommand == 191 or mainCommand == 223:
                self.SkipBytes(48)
                selectObjects = True
            elif mainCommand == 159:
                self.SkipBytes(48)
                hasCommands = False
                selectObjects = True
            else:
                raise Exception(f"Unknown main command: {mainCommand}")
            self.Game["duration"] += ord(self.ReadInt8())
            if hasCommands:
                if (
                        mainCommand == 65
                        or mainCommand == 67
                        or mainCommand == 73
                        or mainCommand == 75
                        or mainCommand == 193
                        or mainCommand == 195
                        or mainCommand == 201
                        or mainCommand == 203
                        or mainCommand == 207
                        or mainCommand == 223
                ):
                    commandsCount = self.ReadInt32()
                else:
                    commandsCount = self.ReadInt8()

                for _ in range(0, commandsCount if isinstance(commandsCount, int) else ord(commandsCount)):
                    self.ExpectedInt8(1)
                    commandId = self.ReadInt32()
                    if commandId == 14:
                        self.SkipBytes(12)
                    self.ExpectedInt8(commandId)
                    playerId = self.ReadInt32()
                    self.ExpectedInt32(-1)
                    self.ExpectedInt32(-1)
                    self.ExpectedInt32(3)
                    unknown0 = self.ReadInt32()
                    if unknown0 == 1:
                        self.ExpectedInt32(playerId)
                    elif unknown0 != 0:
                        raise Exception(f"Unknown0: {unknown0}")
                    unknown1 = self.ReadInt32()
                    selectedCount = self.ReadInt32()
                    selectedIds = []
                    for _ in range(0, selectedCount):
                        selectedIds.append(self.ReadInt32())
                    unknown2 = self.ReadInt32()
                    for _ in range(0, unknown2 * 12):
                        self.SkipBytes(1)
                    unknownCount = self.ReadInt32()
                    unknownList = []
                    for _ in range(0, unknownCount):
                        unknownList.append(self.ReadInt8())
                    self.ExpectedInt8(0)
                    self.ExpectedInt32(0)
                    self.ExpectedInt32(0)
                    self.ExpectedInt32(0)
                    self.ExpectedInt32(-1)
                    self.SkipBytes(4)
                    if commandId == 0:
                        self.ExpectedValue(0, unknown1)
                        self.ExpectedValue(4, unknownCount)
                        if unknown2 == 0:
                            objectId = self.ReadInt32()
                            self.SkipBytes(16)
                            action = {"pid": str(playerId), "duration":
                                                                           self.Game["duration"], "type": "action",
                                                                           "id": unknownList[0],
                                                                           "unknown": unknownList[2],
                                                                           "object_id": objectId,
                                                                           "selected": selectedIds,
                                                                           }
                            #if action not in self.Players[str(playerId)]["actions"]:                                               
                            self.Players[str(playerId)]["actions"].append(action)
                        elif unknown2 == 1:
                            self.SkipBytes(8)
                            self.ExpectedInt8(0)
                            self.ExpectedInt8(0)
                            self.ExpectedInt8(128)
                            self.ExpectedInt8(191)
                            self.ExpectedInt8(0)
                            self.ExpectedInt8(0)
                            self.ExpectedInt8(128)
                            self.ExpectedInt8(191)
                            self.ExpectedInt8(0)
                            self.ExpectedInt8(0)
                            self.ExpectedInt8(128)
                            self.ExpectedInt8(191)
                            action = {"pid": str(playerId), "duration":
                                                                           self.Game["duration"], "type": "way_point",
                                                                           "id": unknownList[0],
                                                                           "unknown": unknownList[2],
                                                                           "selected": selectedIds,
                                                                           }
                            #if action not in self.Players[str(playerId)]["actions"]:
                            self.Players[str(playerId)]["actions"].append(action)
                        else:
                            self.SkipBytes(4)
                            self.ExpectedInt32(0)
                            self.ExpectedInt8(0)
                            self.ExpectedInt8(0)
                            self.ExpectedInt8(128)
                            self.ExpectedInt8(191)
                            self.ExpectedInt8(0)
                            self.ExpectedInt8(0)
                            self.ExpectedInt8(128)
                            self.ExpectedInt8(191)
                            self.ExpectedInt8(0)
                            self.ExpectedInt8(0)
                            self.ExpectedInt8(128)
                            self.ExpectedInt8(191)
                        self.ExpectedInt8(0)
                        self.ExpectedInt8(0)
                        self.ExpectedInt8(128)
                        self.ExpectedInt8(63)
                    elif commandId == 1:
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(4, unknownCount)
                        techId = self.ReadInt32()
                        if self.Game["expansion"] == 0:
                            if str(techId) in self.TechsVanilla:
                                techName = self.TechsVanilla[str(
                                    techId)]["DisplayName"]
                            else:
                                techName = {
                                    "ru": "неизвестно", "en": "unknown"}
                        elif self.Game["expansion"] == 1:
                            if str(techId) in self.TechsTWC:
                                techName = self.TechsTWC[str(
                                    techId)]["DisplayName"]
                            else:
                                techName = {
                                    "ru": "неизвестно", "en": "unknown"}
                        else:
                            if str(techId) in self.TechsTAD:
                                techName = self.TechsTAD[str(
                                    techId)]["DisplayName"]
                            else:
                                techName = {
                                    "ru": "неизвестно", "en": "unknown"}
                        action = {"pid": str(playerId), "duration":
                                                                       self.Game["duration"], "type": "research_tech1",
                                                                       "id": techId,
                                                                       "techName": techName,
                                                                       "selected": selectedIds,
                                                                       }
                        #if action not in self.Players[str(playerId)]["actions"]:
                        self.Players[str(playerId)]["actions"].append(action)
                    elif commandId == 2:
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(4, unknownCount)
                        unitId = self.ReadInt32()
                        shipmentId = self.ReadInt32()

                        self.ExpectedInt8(255)
                        amount = self.ReadInt8()
                        self.SkipBytes(4)
                        if unknown1 == 0:
                            self.ExpectedValue(shipmentId, -1)
                            if self.Game["expansion"] == 0:
                                if str(unitId) in self.UnitsVanilla:
                                    unitName = self.UnitsVanilla[str(
                                        unitId)]["DisplayName"]
                                else:
                                    unitName = {
                                        "ru": "неизвестно", "en": "unknown"}
                            elif self.Game["expansion"] == 1:
                                if str(unitId) in self.UnitsTWC:
                                    unitName = self.UnitsTWC[str(
                                        unitId)]["DisplayName"]
                                else:
                                    unitName = {
                                        "ru": "неизвестно", "en": "unknown"}
                            else:
                                if str(unitId) in self.UnitsTAD:
                                    unitName = self.UnitsTAD[str(
                                        unitId)]["DisplayName"]
                                else:
                                    unitName = {
                                        "ru": "неизвестно", "en": "unknown"}
                            action = {"pid": str(playerId), "duration":
                                                                           self.Game["duration"], "type": "train",
                                                                           "id": unitId,
                                                                           "unitName": unitName,
                                                                           "amount": ord(amount),
                                                                           "selected": selectedIds,
                                                                           }
                            #print("shipment" + str(unitId))
                            #if action not in self.Players[str(playerId)]["actions"]:
                            self.Players[str(playerId)]["actions"].append(action)
                        elif unknown1 == 2:
                            self.ExpectedValue(unitId, -1)
                            self.ExpectedValue(amount, 1)
                            if self.Players[str(playerId)]["selectedDeckId"] != -1:
                                if shipmentId + 1 > len(self.Players[str(playerId)]["decks"][self.Players[str(playerId)]["selectedDeckId"]]["cards"]):
                                    shipmentName = {
                                        "ru": str(shipmentId), "en": str(shipmentId)}
                                else:
                                    if isinstance(self.Players[str(playerId)]["decks"][self.Players[str(playerId)]["selectedDeckId"]]["cards"][shipmentId], dict):
                                        shipmentName = self.Players[str(playerId)]["decks"][self.Players[str(
                                            playerId)]["selectedDeckId"]]["cards"][shipmentId]["DisplayName"]
                                    else:
                                        shipmentName = {
                                            "ru": str(shipmentId), "en": str(shipmentId)}
                            else:
                                if shipmentId + 1 > len(self.Players[str(playerId)]["decks"][0]["cards"]):
                                    shipmentName = {
                                        "ru": str(shipmentId), "en": str(shipmentId)}
                                else:
                                    if isinstance(self.Players[str(playerId)]["decks"][0]["cards"][shipmentId - 1], dict):
                                        shipmentName = self.Players[str(
                                            playerId)]["decks"][0]["cards"][shipmentId]["DisplayName"]
                                    else:
                                        shipmentName = {
                                            "ru": str(shipmentId), "en": str(shipmentId)}
                            action = {"pid": str(playerId), "duration":
                                                                           self.Game["duration"],
                                                                           "type": "shipment",
                                                                           "shipmentName": shipmentName,
                                                                           "id": shipmentId,
                                                                           "selected": selectedIds,
                                                                           }
                            #if action not in self.Players[str(playerId)]["actions"]:
                            #print("shipment" + str(shipmentId))
                            self.Players[str(playerId)]["actions"].append(action)
                        else:
                            raise Exception(f"Unknown1: {unknown1}")
                    elif commandId == 3:
                        self.ExpectedValue(0, unknown1)
                        self.ExpectedValue(4, unknownCount)
                        buildId = self.ReadInt32()
                        self.SkipBytes(24)
                        self.ExpectedInt32(-1)
                        self.ExpectedInt32(-1)
                        self.SkipBytes(8)
                        if self.Game["expansion"] == 0:
                            if str(buildId) in self.UnitsVanilla:
                                unitName = self.UnitsVanilla[str(
                                    buildId)]["DisplayName"]
                            else:
                                unitName = {
                                    "ru": "неизвестно", "en": "unknown"}
                        elif self.Game["expansion"] == 1:
                            if str(buildId) in self.UnitsTWC:
                                unitName = self.UnitsTWC[str(
                                    buildId)]["DisplayName"]
                            else:
                                unitName = {
                                    "ru": "неизвестно", "en": "unknown"}
                        else:
                            if str(buildId) in self.UnitsTAD:
                                unitName = self.UnitsTAD[str(
                                    buildId)]["DisplayName"]
                            else:
                                unitName = {
                                    "ru": "неизвестно", "en": "unknown"}
                        action = {"pid": str(playerId), "duration":
                                                                       self.Game["duration"], "type": "build", "id": buildId, "unitName": unitName, "selected": selectedIds}
                        #if action not in self.Players[str(playerId)]["actions"]:
                        self.Players[str(playerId)]["actions"].append(action)
                    elif commandId == 4:
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(2, unknownCount)
                        self.SkipBytes(25)
                    elif commandId == 6:
                        self.ExpectedValue(4, unknown1)
                        self.ExpectedValue(0, selectedCount)
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(2, unknownCount)
                        self.SkipBytes(32)
                        self.SkipInt32()
                    elif commandId == 7:
                        self.ExpectedValue(0, unknown1)
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(4, unknownCount)
                        self.ExpectedInt8(0)
                    elif commandId == 9:
                        self.ExpectedValue(0, unknown1)
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(2, unknownCount)
                    elif commandId == 12:
                        self.ExpectedValue(1, unknown2)
                        self.ExpectedValue(4, unknownCount)
                        abilityId = self.ReadInt32()
                        self.SkipBytes(24)
                        objectId = self.ReadInt32()
                        powerId = self.ReadInt32()
                        if unknown1 == 0:
                            Type = "ability"
                        elif unknown1 == 3:
                            self.ExpectedValue(abilityId, -1)
                            Type = "special_power"
                        else:
                            raise Exception(f"Unknown1: {unknown1}")
                        action = {"pid": str(playerId), "duration":
                                                                       self.Game["duration"], "type": Type,
                                                                       "id": powerId,
                                                                       "object_id": objectId,
                                                                       "selected": selectedIds,
                                                                       }
                        #if action not in self.Players[str(playerId)]["actions"]:
                        self.Players[str(playerId)]["actions"].append(action)
                    elif commandId == 13:
                        self.ExpectedValue(3, unknown1)
                        self.ExpectedValue(1, selectedCount)
                        self.ExpectedValue(playerId, selectedIds[0])
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(2, unknownCount)
                        self.SkipBytes(4)
                        self.ExpectedInt32(0)
                        self.SkipBytes(4)
                    elif commandId == 14:  # cancel queue of shipment
                        self.ExpectedValue(4, unknownCount)
                        #print(self.Data[self.Offset:self.Offset+32])
                    elif commandId == 16:
                        self.ExpectedValue(3, unknown1)
                        self.ExpectedValue(0, selectedCount)
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(2, unknownCount)
                        self.SkipBytes(4)
                        self.ExpectedInt32(playerId)
                        self.SkipBytes(4)
                        self.Players[str(playerId)]["is_resigned"] += 1
                        action = {"pid": str(playerId), "duration":
                                                                       self.Game["duration"], "type": "resigned"}
                        #if action not in self.Players[str(playerId)]["actions"]:
                        self.Players[str(playerId)]["actions"].append(action)

                    elif commandId == 18:
                        self.ExpectedValue(0, unknown1)
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(2, unknownCount)
                        self.SkipBytes(4)
                    elif commandId == 19:
                        self.ExpectedValue(4, unknown1)
                        self.ExpectedValue(0, selectedCount)
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(2, unknownCount)
                        self.SkipBytes(16)
                    elif commandId == 23:
                        self.ExpectedValue(0, unknown1)
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(2, unknownCount)
                        self.SkipBytes(5)
                    elif commandId == 24:
                        self.ExpectedValue(0, unknown1)
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(2, unknownCount)
                        self.SkipBytes(12)
                    elif commandId == 25:
                        self.ExpectedValue(0, unknown1)
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(2, unknownCount)
                        self.SkipBytes(1)
                        self.ExpectedInt8(255)
                        self.SkipBytes(4)
                    elif commandId == 26:
                        self.ExpectedValue(3, unknown1)
                        self.ExpectedValue(0, selectedCount)
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(2, unknownCount)
                        withPlayerId = self.ReadInt8()
                        diplomacy = self.ReadInt8()
                        self.SkipBytes(2)
                        action = {"pid": str(playerId), "duration":
                                                                       self.Game["duration"], "type": "diplomacy",
                                                                       "id": ord(diplomacy),
                                                                       "player_id": ord(withPlayerId),
                                                                       }
                        #if action not in self.Players[str(playerId)]["actions"]:
                        self.Players[str(playerId)]["actions"].append(action)
                    elif commandId == 34:
                        self.ExpectedValue(0, unknown1)
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(4, unknownCount)
                    elif commandId == 35:
                        self.ExpectedValue(0, unknown1)
                        self.ExpectedValue(2, unknownCount)
                        self.SkipBytes(4)
                    elif commandId == 37:
                        self.ExpectedValue(0, unknown1)
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(2, unknownCount)
                        self.SkipBytes(5)
                    elif commandId == 41:
                        self.ExpectedValue(3, unknown1)
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(2, unknownCount)
                        control1 = self.ReadInt32()
                        control2 = self.ReadInt32()
                        control3 = self.ReadInt32()
                        self.ExpectedInt32(-1)
                        self.ExpectedInt32(0)
                        unknown1 = self.ReadInt32()
                        if control1 == 1:
                            if control2 == 1:
                                self.ExpectedValue(5, control3)
                            else:
                                self.ExpectedValue(0, control3)
                            self.ExpectedValue(-1, unknown1)
                            self.ExpectedInt32(0)
                            unknown2 = self.ReadInt32()
                            if unknown2 == 1:
                                unknown3 = self.ReadInt32()
                            else:
                                unknown3 = None
                            self.ExpectedInt8(1)
                            if unknown2 == 1:
                                self.ExpectedInt8(0)
                                self.ExpectedInt8(0)
                                self.ExpectedInt8(128)
                                self.ExpectedInt8(191)
                                self.ExpectedInt8(0)
                                self.ExpectedInt8(0)
                                self.ExpectedInt8(128)
                                self.ExpectedInt8(191)
                                self.ExpectedInt8(0)
                                self.ExpectedInt8(0)
                                self.ExpectedInt8(128)
                                self.ExpectedInt8(191)
                            else:
                                self.SkipBytes(12)
                            if control2 == 1:
                                action = {"pid": str(playerId), "duration":
                                                                               self.Game["duration"], "type": "allies_request",
                                                                               "request": "flare",
                                                                               "players": selectedIds,
                                                                               }
                                #if action not in self.Players[str(playerId)]["actions"]:
                                self.Players[str(playerId)]["actions"].append(action)
                            elif control2 == 3:
                                if unknown3 == 0:
                                    resource = "gold"
                                elif unknown3 == 1:
                                    resource = "wood"
                                elif unknown3 == 2:
                                    resource = "food"
                                else:
                                    raise Exception(f"unknown3: {unknown3}")
                                action = {"pid": str(playerId), "duration":
                                                                               self.Game["duration"],
                                                                               "type": "allies_request",
                                                                               "request": "send",
                                                                               "resource": resource,
                                                                               "players": selectedIds,
                                                                               }
                                #if action not in self.Players[str(playerId)]["actions"]:
                                self.Players[str(playerId)]["actions"].append(action)
                            elif control2 == 4:
                                if unknown3 == 0:
                                    resource = "gold"
                                elif unknown3 == 1:
                                    resource = "wood"
                                elif unknown3 == 2:
                                    resource = "food"
                                else:
                                    raise Exception(f"unknown3: {unknown3}")
                                action = {"pid": str(playerId), "duration":
                                                                               self.Game["duration"], "type": "allies_request",
                                                                               "request": "overtime",
                                                                               "resource": resource,
                                                                               "players": selectedIds,
                                                                               }
                                #if action not in self.Players[str(playerId)]["actions"]:
                                self.Players[str(playerId)]["actions"].append(action)
                            elif control2 == 5:
                                action = {"pid": str(playerId), "duration":
                                                                               self.Game["duration"], "type": "allies_request",
                                                                               "request": "stop",
                                                                               "players": selectedIds,
                                                                               }
                                #if action not in self.Players[str(playerId)]["actions"]:
                                self.Players[str(playerId)]["actions"].append(action)
                            elif control2 == 7:
                                if unknown3 == 1482:
                                    unit = "infantry"
                                elif unknown3 == 1483:
                                    unit = "cavalry"
                                elif unknown3 == 1534:
                                    unit = "artillery"
                                else:
                                    raise Exception(f"unknown3: {unknown3}")
                                action = {"pid": str(playerId), "duration":
                                                                               self.Game["duration"], "type": "allies_request",
                                                                               "request": "build",
                                                                               "unit": unit,
                                                                               "players": selectedIds,
                                                                               }
                                #if action not in self.Players[str(playerId)]["actions"]:
                                self.Players[str(playerId)]["actions"].append(action)
                            elif control2 == 8:
                                if unknown3 == 1:
                                    action = "aggressivity"
                                elif unknown3 == 2:
                                    action = "economy"
                                elif unknown3 == 3:
                                    action = "defensive"
                                else:
                                    raise Exception(f"unknown3: {unknown3}")
                                action = {"pid": str(playerId), "duration":
                                                                               self.Game["duration"], "type": "allies_request",
                                                                               "request": "start",
                                                                               "action": action,
                                                                               "players": selectedIds,
                                                                               }
                                #if action not in self.Players[str(playerId)]["actions"]: 
                                self.Players[str(playerId)]["actions"].append(action)
                            else:
                                break

                        elif control1 == 3:
                            self.ExpectedValue(0, control2)
                            self.ExpectedValue(0, control3)
                            self.ExpectedInt32(0)
                            self.ExpectedInt32(0)
                            self.SkipBytes(13)
                        else:
                            raise Exception(f"control1: {control1}")
                    elif commandId == 44:
                        self.ExpectedValue(3, unknown1)
                        self.ExpectedValue(1, selectedCount)
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(2, unknownCount)
                        self.SkipBytes(8)
                    elif commandId == 46:  # / Cancel queue of unit/tech
                        self.ExpectedValue(0, unknown1)
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(2, unknownCount)
                        self.SkipBytes(8)
                        #print(self.Data[self.Offset:self.Offset+4])
                    elif commandId == 48:
                        self.ExpectedValue(3, unknown1)
                        self.ExpectedValue(0, selectedCount)
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(2, unknownCount)
                        self.SkipBytes(9)
                    elif commandId == 53:
                        self.ExpectedValue(0, unknown1)
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(4, unknownCount)
                        self.SkipBytes(8)
                    elif commandId == 57:
                        self.ExpectedValue(3, unknown1)
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(4, unknownCount)
                        objectId = self.ReadInt32()
                        self.SkipBytes(4)
                        resource = self.ReadInt32()
                        action = {"pid": str(playerId), "duration":
                                                                       self.Game["duration"], "type": "change_trade_route_resource",
                                                                       "object_id": objectId,
                                                                       "resource": resource,
                                                                       "selected": selectedIds,
                                                                       }
                        #if action not in self.Players[str(playerId)]["actions"]:
                        self.Players[str(playerId)]["actions"].append(action)
                    elif commandId == 58:
                        self.ExpectedValue(3, unknown1)
                        self.ExpectedValue(0, selectedCount)
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(2, unknownCount)
                        self.SkipBytes(4)
                    elif commandId == 61:
                        self.ExpectedValue(3, unknown1)
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(2, unknownCount)
                        objectId = self.ReadInt32()
                        action = {"pid": str(playerId), "duration":
                                                                       self.Game["duration"], "type": "shipments_way_point",
                                                                       "object_id": objectId,
                                                                       "selected": selectedIds,
                                                                       }
                        #if action not in self.Players[str(playerId)]["actions"]:
                        self.Players[str(playerId)]["actions"].append(action)
                    elif commandId == 62:
                        self.ExpectedValue(0, unknown1)
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(4, unknownCount)
                        self.SkipBytes(4)
                    elif commandId == 63:
                        self.ExpectedValue(3, unknown1)
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(2, unknownCount)
                        unitId = self.ReadInt32()
                        objectId = self.ReadInt32()
                        amount = self.ReadInt32()
                        if self.Game["expansion"] == 0:
                            if str(unitId) in self.UnitsVanilla:
                                unitName = self.UnitsVanilla[str(
                                    unitId)]["DisplayName"]
                            else:
                                unitName = {
                                    "ru": "неизвестно", "en": "unknown"}
                        elif self.Game["expansion"] == 1:
                            if str(unitId) in self.UnitsTWC:
                                unitName = self.UnitsTWC[str(
                                    unitId)]["DisplayName"]
                            else:
                                unitName = {
                                    "ru": "неизвестно", "en": "unknown"}
                        else:
                            if str(unitId) in self.UnitsTAD:
                                unitName = self.UnitsTAD[str(
                                    unitId)]["DisplayName"]
                            else:
                                unitName = {
                                    "ru": "неизвестно", "en": "unknown"}
                        action = {"pid": str(playerId), "duration":
                                                                       self.Game["duration"], "type": "spawn_unit",
                                                                       "id": unitId,
                                                                       "unitName": unitName,
                                                                       "object_id": objectId,
                                                                       "amount": amount,
                                                                       "selected": selectedIds,
                                                                       }
                        #if action not in self.Players[str(playerId)]["actions"]:
                        self.Players[str(playerId)]["actions"].append(action)
                    elif commandId == 64:
                        self.ExpectedValue(3, unknown1)
                        self.ExpectedValue(0, selectedCount)
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(2, unknownCount)
                    elif commandId == 65:
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(4, unknownCount)
                        techId = self.ReadInt32()
                        if unknown1 == 0:
                            Type = "research_tech2"
                        elif unknown1 == 2:
                            Type = "research_tech3"
                        else:
                            raise Exception(f"Unknown1: {unknown1}")
                        if self.Game["expansion"] == 0:
                            if str(techId) in self.TechsVanilla:
                                techName = self.TechsVanilla[str(
                                    techId)]["DisplayName"]
                            else:
                                techName = {
                                    "ru": "неизвестно", "en": "unknown"}
                        elif self.Game["expansion"] == 1:
                            if str(techId) in self.TechsTWC:
                                techName = self.TechsTWC[str(
                                    techId)]["DisplayName"]
                            else:
                                techName = {
                                    "ru": "неизвестно", "en": "unknown"}
                        else:
                            if str(techId) in self.TechsTAD:
                                techName = self.TechsTAD[str(
                                    techId)]["DisplayName"]
                            else:
                                techName = {
                                    "ru": "неизвестно", "en": "unknown"}
                        action = {"pid": str(playerId), "duration":
                                                                       self.Game["duration"], "type": Type, "techName": techName, "id": techId, "selected": selectedIds}
                        #if action not in self.Players[str(playerId)]["actions"]:
                        self.Players[str(playerId)]["actions"].append(action)
                    elif commandId == 66:
                        self.ExpectedValue(2, unknown1)
                        self.ExpectedValue(1, selectedCount)
                        self.ExpectedValue(playerId, selectedIds[0])
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(4, unknownCount)
                        deckId = self.ReadInt32()
                        self.SkipBytes(4)
                        self.Players[str(playerId)]["selectedDeckId"] = deckId
                        action = {"pid": str(playerId), "duration":
                                                                       self.Game["duration"], "type": "pick_deck", "deckName": self.Players[str(playerId)]["decks"][deckId]["name"],  "id": deckId, "selected": selectedIds}
                        #if action not in self.Players[str(playerId)]["actions"]:
                        self.Players[str(playerId)]["actions"].append(action)
                    elif commandId == 67:
                        self.ExpectedValue(3, unknown1)
                        self.ExpectedValue(0, selectedCount)
                        self.ExpectedValue(0, unknown2)
                        self.ExpectedValue(4, unknownCount)
                        self.SkipBytes(12)
                    else:
                        raise Exception(f"Unknown command: {commandId}")
            if selectObjects:
                selectedCount = ord(self.ReadInt8())
                if selectedCount:
                    selectedIds = []
                    for _ in range(0, selectedCount):
                        selectedIds.append(self.ReadInt32())
                    action = {"pid": str(ord(self.Game["view_point"])), "duration":
                                                                                       self.Game["duration"], "type": "selected", "ids": selectedIds}
                    #if action not in self.Players[str(ord(self.Game["view_point"]))]["actions"]:                                                        
                    #    self.Players[str(ord(self.Game["view_point"]))]["actions"].append(action)
            try:
                resignCount = ord(self.ReadInt8())
            except:
                pass
            resignList = []
            for _ in range(0, resignCount):
                try:
                    resignList.append(self.ReadInt8())
                except:
                    pass

    def ExpectedValue(self, expectedValue, value):
        if isinstance(expectedValue, bytes):
            expectedValue = ord(expectedValue)
        if isinstance(value, bytes):
            value = ord(value)
        if expectedValue != value:
            raise Exception(
                f"Invalid value: {value}, expected: {expectedValue}")

    def ExpectedInt8(self, expectedValue):
        value = self.ReadInt8()
        self.ExpectedValue(expectedValue, value)

    def ExpectedInt16(self, expectedValue):
        value = self.ReadInt16()
        self.ExpectedValue(expectedValue, value)

    def ExpectedInt32(self, expectedValue):
        value = self.ReadInt32()
        self.ExpectedValue(expectedValue, value)

    def ExpectedFloat(self, expectedValue):
        value = self.ReadFloat()
        self.ExpectedValue(expectedValue, value)

    def ExpectedString(self, expectedValue):
        value = self.ReadString()
        self.ExpectedValue(expectedValue, value)

    def GoToOffset(self, offset):
        self.Offset = offset

    def ReadInt8(self):
        return self.ReadData("c", 1)

    def ReadInt16(self):
        return self.ReadData("v", 2)

    def ReadInt32(self):
        return self.ReadData("l", 4)

    def ReadFloat(self):
        return self.ReadData("f", 4)

    def SkipInt32(self):
        self.Offset += 4

    def ResetOffset(self):
        self.Offset = 0

    def ReadString(self):
        length = self.ReadInt32()
        if length:
            length = length * 2
            Str = self.Data[self.Offset: self.Offset + length]
            self.Offset += length
            return Str.decode("UTF-16le")
        else:
            return None

    def Search(
            self, needle, currentOffset=False, addNeedleLength=False, needEncode=True
    ):
        if needEncode:
            self.Offset = self.Data.find(
                needle.encode("utf-16le"), self.Offset if currentOffset else 0
            )
        else:
            self.Offset = self.Data.find(
                needle, self.Offset if currentOffset else 0)
        if self.Offset > -1:
            if addNeedleLength:
                if needEncode:
                    self.Offset += len(needle) * 2
                else:
                    self.Offset += len(needle)
            return True
        else:
            return False


class RecordGameSignals(QObject):
    infoSignal = pyqtSignal(dict)


class RecordGame(QRunnable):
    def __init__(self, fileName):
        super().__init__()
        self.fileName = fileName
        self.signals = RecordGameSignals()

    def run(self):
        r = RecordParser()
        try:
            r.Parser(self.fileName)
            self.signals.infoSignal.emit(
                {
                    "Game": r.Game,
                    "Players": r.Players,
                }
            )
        except Exception as e:
            # print(e)
            self.signals.infoSignal.emit(
                {
                    "Game": {},
                    "Players": {},
                }
            )
