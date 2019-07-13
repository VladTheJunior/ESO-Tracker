from PyQt5.QtCore import (
    QAbstractListModel,
    Qt,
    QModelIndex,
    QVariant,
    QSortFilterProxyModel

)
from datetime import timedelta

from Constants import playerColors, playerBColors
import locale
import localization


class PlayerActionsListModel(QAbstractListModel):
    def __init__(self, data=[], additionalInfo={}, parent=None):
        self.__data = data
        self.info = additionalInfo
        self.lang = list(locale.getdefaultlocale())[0][0:2]

        if self.lang == "ru":
            self.loc = localization.ru
        else:
            self.loc = localization.en
        QAbstractListModel.__init__(self, parent)

    def rowCount(self, parent=QModelIndex()):
        return len(self.__data)

    def data(self, index, role):
        if index.isValid():
            data = self.__data[index.row()]
            if role == Qt.UserRole:
                return {"duration": data["duration"], "action": data["type"]}
            if role == Qt.ForegroundRole:
                return playerColors[self.info[data["pid"]]["color"] - 1]
            if role == Qt.BackgroundColorRole:
                return playerBColors[self.info[data["pid"]]["color"] - 1]
            if role == Qt.DisplayRole:
                if data["type"] == "resigned":
                    return str(timedelta(milliseconds=data["duration"])) + " (" + self.info[data["pid"]]["name"] + ") − " + self.loc[data["type"]]
                elif data["type"] == "spawn_unit":
                    return str(timedelta(milliseconds=data["duration"])) + " (" + self.info[data["pid"]]["name"] + ") − " + self.loc[data["type"]] + data["unitName"][self.loc["language"]] + "(x" + str(data["amount"]) + ")"
                elif data["type"] == "shipment":
                    return str(timedelta(milliseconds=data["duration"])) + " (" + self.info[data["pid"]]["name"] + ") − " + self.loc[data["type"]] + data["shipmentName"][self.loc["language"]]
                elif data["type"] == "build":
                    return str(timedelta(milliseconds=data["duration"])) + " (" + self.info[data["pid"]]["name"] + ") − " + self.loc[data["type"]] + data["unitName"][self.loc["language"]]
                elif data["type"] == "pick_deck":
                    return str(timedelta(milliseconds=data["duration"])) + " (" + self.info[data["pid"]]["name"] + ") − " + self.loc[data["type"]] + data["deckName"]
                elif data["type"] == "research_tech1" or data["type"] == "research_tech2" or data["type"] == "research_tech3":
                    return str(timedelta(milliseconds=data["duration"])) + " (" + self.info[data["pid"]]["name"] + ") − " + self.loc[data["type"]] + data["techName"][self.loc["language"]]
                elif data["type"] == "train":
                    return str(timedelta(milliseconds=data["duration"])) + " (" + self.info[data["pid"]]["name"] + ") − " + self.loc[data["type"]] + data["unitName"][self.loc["language"]] + "(x" + str(data["amount"]) + ")"
        else:
            return QVariant()


class PlayerActionsProxyModel(QSortFilterProxyModel):
    def __init__(self, filters, model, parent=None):
        QSortFilterProxyModel.__init__(self, parent)
        self.filter = filters
        self.setSourceModel(model)

    def lessThan(self, top, bottom):
        topTime = top.data(Qt.UserRole)["duration"]
        bottomTime = bottom.data(Qt.UserRole)["duration"]
        return topTime < bottomTime

    def filterAcceptsRow(self, sourceRow, sourceParent):
        index = self.sourceModel().index(sourceRow, 0, sourceParent)
        if index.isValid():
            action = index.data(Qt.UserRole)["action"]
            color = index.data(Qt.ForegroundRole)
            return (
                color in self.filter["colors"] and action in self.filter["actions"]
            )
        else:
            return True
