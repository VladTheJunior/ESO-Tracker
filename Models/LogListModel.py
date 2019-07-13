from PyQt5.QtCore import (
    QAbstractListModel,
    Qt,
    QModelIndex,
    QVariant,
    QSortFilterProxyModel,


)
from PyQt5.QtGui import QColor
from Constants import clBlack, clBlue, clGreen, clRed, clViolet


class LogListModel(QAbstractListModel):
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
            if role == Qt.ForegroundRole:
                return QColor(data["color"].replace("#e5e5e5", clBlack))
            if role == Qt.DisplayRole:
                return data["text"]
        else:
            return QVariant()


class LogFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, Filter, model, parent=None):
        QSortFilterProxyModel.__init__(self, parent)
        self.filter = Filter
        self.setSourceModel(model)

    def setFilterPattern(self, pattern):
        self.filter = pattern

    def filterAcceptsRow(self, sourceRow, sourceParent):
        index = self.sourceModel().index(sourceRow, 0, sourceParent)
        if index.isValid():
            text = index.data(Qt.DisplayRole)
            color = index.data(Qt.ForegroundRole)
            if self.filter["text"] == "":
                return color in self.filter["colors"]
            else:
                return (
                    self.filter["text"].lower() in text.lower()
                    and color in self.filter["colors"]
                )
        else:
            return True
