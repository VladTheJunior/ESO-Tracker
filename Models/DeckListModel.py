from PyQt5.QtCore import (
    QAbstractListModel,
    Qt,
    QModelIndex,
    QVariant,

)
from PyQt5.QtGui import QFont, QPixmap
import locale
import localization
import os


class DeckListModel(QAbstractListModel):
    def __init__(self, data=[], parent=None):
        self.__data = data
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
            if "aName" in data:
                if role == Qt.FontRole:
                    return QFont("Consolas", 16, weight=QFont.Bold)
                if role == Qt.DisplayRole:
                    return data["aName"]
            elif "pName" in data:
                if role == Qt.FontRole:
                    return QFont("Consolas", 20, weight=QFont.Bold)
                if role == Qt.TextAlignmentRole:
                    return Qt.AlignCenter
                if role == Qt.DisplayRole:
                    return data["pName"] + " - " + data["dName"]
            else:
                if role == Qt.DecorationRole:
                    return QPixmap(os.path.join("Cards", data["Icon"].split("\\")[-1])).scaledToWidth(64, Qt.SmoothTransformation)
                if role == Qt.DisplayRole:
                    text = data["DisplayName"][self.loc["language"]]
                    if data["RolloverText"][self.loc["language"]] is not None:
                        text = text + "\n" + \
                            data["RolloverText"][self.loc["language"]]
                    return text
        else:
            return QVariant()
