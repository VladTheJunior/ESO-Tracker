from PyQt5.QtCore import (
    QAbstractListModel,
    Qt,
    QModelIndex,
    QVariant,
    QSortFilterProxyModel,
    
    
)
from PyQt5.QtGui import QColor, QPixmap, QImage
import ipaddress
import base64

class IPandESOListModel(QAbstractListModel):
    def __init__(self, data=[], parent=None):
        self.__data = data
        QAbstractListModel.__init__(self, parent)

    def rowCount(self, parent=QModelIndex()):
        return len(self.__data)

    def insertRecord(self, record):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.__data.append(record)
        self.endInsertRows()

    def data(self, index, role):
        if index.isValid():
            data = self.__data[index.row()]
            if role == Qt.ToolTipRole:
                if "IPInfo" in data:
                    return data["IPInfo"]["Country"] + ", " + data["IPInfo"]["City"]

            if role == Qt.DecorationRole:
                if "IPInfo" in data:
                    if data["IPInfo"]["Flag"] == "":
                        return QColor("transparent")
                    image = QImage()
                    image.loadFromData(base64.decodestring(data["IPInfo"]["Flag"].encode("ascii")))
                    return QPixmap(image)
                else:
                    return QColor("transparent")
            if role == Qt.DisplayRole:
                return data["IP"] + " : " + data["ESO"]
        else:
            return QVariant()


class IPandESOFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, Filter, model, parent=None):
        QSortFilterProxyModel.__init__(self, parent)
        self.filter = Filter
        self.setSourceModel(model)

    def setFilterPattern(self, pattern):
        self.filter = pattern

    def lessThan(self, top, bottom):
        topIP = top.data().split(" : ")[0]
        bottomIP = bottom.data().split(" : ")[0]
        return ipaddress.ip_address(topIP) < ipaddress.ip_address(bottomIP)


    def filterAcceptsRow(self, sourceRow, sourceParent):
        index = self.sourceModel().index(sourceRow, 0, sourceParent)
        if index.isValid():
            text = index.data(Qt.DisplayRole)
            if self.filter == "":
                return True
            else:
                return (
                    self.filter.lower() in text.lower()
                )
        else:
            return True
