from PyQt5.QtCore import (
	QAbstractListModel,
	Qt,
	QModelIndex,
	QVariant,  
	QSortFilterProxyModel
	
)
from PyQt5.QtGui import QColor, QPixmap, QImage
import base64
from datetime import datetime

class LobbyListModel(QAbstractListModel):
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
			if role == Qt.UserRole:
					return data["LastUpdate"]
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
				return data["IP"] + " : " + data["RTT"]
		else:
			return QVariant()


class LobbyFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, model, parent=None):
        QSortFilterProxyModel.__init__(self, parent)
        self.setSourceModel(model)


    def filterAcceptsRow(self, sourceRow, sourceParent):
        index = self.sourceModel().index(sourceRow, 0, sourceParent)
        if index.isValid():
            date = index.data(Qt.UserRole)
            return (datetime.now() - date).total_seconds() < 3
