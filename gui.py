import json
import os
import os.path
import pkgutil
import sys
import ipaddress
import locale
from datetime import datetime, timezone
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (
    QObject,
    QPoint,
    QRunnable,
    QSettings,
    Qt,
    QThread,
    QThreadPool,
    QTimer,
    pyqtSignal,
)
from PyQt5.QtGui import QColor, QFont, QIcon, QImage
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QDesktopWidget,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QWidget,
)

import localization
import Styles
from Constants import clBlack, clBlue, clGreen, clRed, clViolet
from IPInfo import IPInfo
from PingIP import pingIP
from SniffThread import SniffThread
from Speech import Speech


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.lang = list(locale.getdefaultlocale())[0][0:2]

        if self.lang == "ru":
            self.loc = localization.ru
        else:
            self.loc = localization.en
        self.initUI()

    def getPath(self):
        if getattr(sys, "frozen", False):
            # we are running in a bundle
            return os.path.join(sys._MEIPASS, "").replace("\\", "/")
        else:
            # we are running in a normal Python environment
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), "").replace(
                "\\", "/"
            )

    def getIconPath(self):
        if getattr(sys, "frozen", False):
            # we are running in a bundle
            return os.path.join(sys._MEIPASS, "icon.ico")
        else:
            # we are running in a normal Python environment
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")

    def initUI(self):
        self.jsonPackets = []
        self.jsonIPandNames = []
        self.IPinLobby = []
        self.pool = QThreadPool()
        self.poolIPInfo = QThreadPool()
        self.poolTaunts = QThreadPool()
        self.poolSpeech = QThreadPool()
        self.poolSpeech.setMaxThreadCount(1)

        QtGui.QFontDatabase.addApplicationFont(
            self.getPath() + "Visuals/Fonts/MTCORSVA.TTF"
        )
        QtGui.QFontDatabase.addApplicationFont(
            self.getPath() + "Visuals/Fonts/formal-436-bt-5947cc2c8b950.ttf"
        )

        self.oldPos = self.pos()
        self.mainWindow = QWidget(self)
        self.mainWindow.setObjectName("MainWindow")
        self.mainWindow.setStyleSheet(Styles.stylesheet.format(path=self.getPath()))
        grid = QGridLayout()
        self.mainWindow.setLayout(grid)

        self.TopLeft = QWidget()

        self.TopLeft.setObjectName("TopLeft")
        self.TopLeft.setFixedSize(24, 24)
        grid.addWidget(self.TopLeft, 0, 0)

        self.Left = QWidget()
        self.Left.setFixedSize(24, 400)
        self.Left.setObjectName("Left")

        grid.addWidget(self.Left, 2, 0)

        self.TopLeftBottom = QWidget()
        self.TopLeftBottom.setFixedSize(24, 82)
        self.TopLeftBottom.setObjectName("TopLeftBottom")

        grid.addWidget(self.TopLeftBottom, 1, 0)

        self.BottomLeftTop = QWidget()
        self.BottomLeftTop.setFixedSize(24, 82)
        self.BottomLeftTop.setObjectName("BottomLeftTop")

        grid.addWidget(self.BottomLeftTop, 3, 0, Qt.AlignBottom)

        self.BottomLeft = QWidget()
        self.BottomLeft.setObjectName("BottomLeft")
        self.BottomLeft.setFixedSize(24, 24)
        grid.addWidget(self.BottomLeft, 4, 0)

        self.BottomLeftRight = QWidget()
        self.BottomLeftRight.setObjectName("BottomLeftRight")
        self.BottomLeftRight.setFixedSize(82, 24)
        grid.addWidget(self.BottomLeftRight, 4, 1)

        self.Bottom = QWidget()
        self.Bottom.setObjectName("Bottom")
        self.Bottom.setFixedSize(1250, 24)
        grid.addWidget(self.Bottom, 4, 2)

        self.Right = QWidget()
        self.Right.setObjectName("Right")
        self.Right.setFixedSize(24, 400)
        grid.addWidget(self.Right, 2, 4)

        self.BottomRightLeft = QWidget()
        self.BottomRightLeft.setObjectName("BottomRightLeft")
        self.BottomRightLeft.setFixedSize(82, 24)
        grid.addWidget(self.BottomRightLeft, 4, 3)

        self.BottomRight = QWidget()
        self.BottomRight.setObjectName("BottomRight")
        self.BottomRight.setFixedSize(24, 24)
        grid.addWidget(self.BottomRight, 4, 4)

        self.BottomRightTop = QWidget()
        self.BottomRightTop.setObjectName("BottomRightTop")
        self.BottomRightTop.setFixedSize(24, 82)
        grid.addWidget(self.BottomRightTop, 3, 4)

        self.Top = QWidget()
        self.Top.setObjectName("Top")
        self.Top.setFixedSize(1250, 24)
        grid.addWidget(self.Top, 0, 2)

        self.TopRight = QPushButton()
        self.TopRight.setObjectName("TopRight")
        self.TopRight.setFixedSize(24, 24)
        self.TopRight.clicked.connect(self.close)
        grid.addWidget(self.TopRight, 0, 4)

        self.TopRightLeft = QWidget()
        self.TopRightLeft.setObjectName("TopRightLeft")
        self.TopRightLeft.setFixedSize(82, 24)
        grid.addWidget(self.TopRightLeft, 0, 3)

        self.TopRightBottom = QWidget()
        self.TopRightBottom.setObjectName("TopRightBottom")
        self.TopRightBottom.setFixedSize(24, 82)
        grid.addWidget(self.TopRightBottom, 1, 4)

        self.TopLeftRight = QWidget()
        self.TopLeftRight.setObjectName("TopLeftRight")
        self.TopLeftRight.setFixedSize(82, 24)

        self.Title = QLabel("ESO Packet Tracker")
        self.Title.setObjectName("Title")
        self.Title.setAlignment(Qt.AlignCenter)
        self.Title.setFixedSize(226, 24)
        grid.addWidget(self.Title, 0, 2)

        grid.addWidget(self.TopLeftRight, 0, 1)

        self.Content = QWidget()
        ContentLayout = QGridLayout()
        self.Content.setLayout(ContentLayout)

        self.w = QListWidget()
        self.w.setFont(QFont("Consolas", 11, weight=QFont.Bold))
        ContentLayout.addWidget(self.w, 2, 1)
        self.lobby = QListWidget()
        self.lobby.setStyleSheet("color:" + clBlack)
        self.lobby.mousePressEvent = self.changeIPandNameFilter2
        self.lobby.setFixedWidth(250)
        self.lobby.setFont(QFont("Consolas", 11, weight=QFont.Bold))
        ContentLayout.addWidget(self.lobby, 2, 2)

        self.IPandNames = QListWidget()
        self.IPandNames.setFixedWidth(300)
        self.IPandNames.setStyleSheet("color:" + clBlack)
        self.IPandNames.mousePressEvent = self.changeIPandNameFilter1
        self.IPandNames.setFont(QFont("Consolas", 11, weight=QFont.Bold))
        ContentLayout.addWidget(self.IPandNames, 2, 3)

        l = QLabel(self.loc["plogs"])
        ContentLayout.addWidget(l, 1, 1)

        l2 = QLabel(self.loc["playersinlobby"])
        ContentLayout.addWidget(l2, 1, 2)

        l3 = QLabel(self.loc["ipandeso"])
        ContentLayout.addWidget(l3, 1, 3)

        self.groupBox = QWidget()

        gridBox = QGridLayout()

        settings = QSettings("XaKOps", "ESO Packet Tracker")
        cs1 = settings.value("box1", True, type=bool)
        cs2 = settings.value("box2", True, type=bool)
        cs3 = settings.value("box3", True, type=bool)
        cs4 = settings.value("box4", True, type=bool)
        cs5 = settings.value("box5", True, type=bool)

        cs6 = settings.value("box6", True, type=bool)
        cs7 = settings.value("box7", True, type=bool)
        cs8 = settings.value("box8", True, type=bool)
        cs9 = settings.value("box9", True, type=bool)

        self.colorFilters = QWidget()
        gridBox3 = QGridLayout()

        self.Colors = QLabel(self.loc["Colors"])
        gridBox.addWidget(self.Colors, 1, 0)

        self.cb1 = QCheckBox(self.loc["black"])
        self.cb1.setChecked(cs1)
        self.cb1.setStyleSheet("color:" + clBlack)
        self.cb1.clicked.connect(self.filterClicked)
        gridBox3.addWidget(self.cb1, 0, 1)

        self.cb2 = QCheckBox(self.loc["violet"])
        self.cb2.setChecked(cs2)
        self.cb2.setStyleSheet("color:" + clViolet)
        self.cb2.clicked.connect(self.filterClicked)
        gridBox3.addWidget(self.cb2, 0, 2)

        self.cb3 = QCheckBox(self.loc["blue"])
        self.cb3.setChecked(cs3)
        self.cb3.setStyleSheet("color:" + clBlue)
        self.cb3.clicked.connect(self.filterClicked)
        gridBox3.addWidget(self.cb3, 0, 3)

        self.cb4 = QCheckBox(self.loc["green"])
        self.cb4.setChecked(cs4)
        self.cb4.setStyleSheet("color:" + clGreen)
        self.cb4.clicked.connect(self.filterClicked)
        gridBox3.addWidget(self.cb4, 0, 4)

        self.cb5 = QCheckBox(self.loc["red"])
        self.cb5.setStyleSheet("color:" + clRed)
        self.cb5.setChecked(cs5)
        self.cb5.clicked.connect(self.filterClicked)
        gridBox3.addWidget(self.cb5, 0, 5)

        self.colorFilters.setLayout(gridBox3)
        gridBox.addWidget(self.colorFilters, 1, 1, 1, 4)

        self.Sounds = QLabel(self.loc["sounds"])
        gridBox.addWidget(self.Sounds, 2, 0)

        self.cb6 = QCheckBox(self.loc["Notifications"])
        self.cb6.setChecked(cs6)
        self.cb6.clicked.connect(self.soundsFilter)
        gridBox.addWidget(self.cb6, 2, 1)

        self.cb7 = QCheckBox(self.loc["connection"])
        self.cb7.setChecked(cs7)
        self.cb7.clicked.connect(self.soundsFilter)
        gridBox.addWidget(self.cb7, 2, 4)

        self.cb8 = QCheckBox(self.loc["Friends"])
        self.cb8.setChecked(cs8)
        self.cb8.clicked.connect(self.soundsFilter)
        gridBox.addWidget(self.cb8, 2, 3)

        self.cb9 = QCheckBox(self.loc["Messages"])
        self.cb9.setChecked(cs9)
        self.cb9.clicked.connect(self.soundsFilter)
        gridBox.addWidget(self.cb9, 2, 2)

        self.filterLable = QLabel(self.loc["filter"])
        gridBox.addWidget(self.filterLable, 0, 0)
        self.filter = QLineEdit(self)
        self.filter.textChanged.connect(self.filterClicked)
        gridBox.addWidget(self.filter, 0, 1, 1, 4)

        self.groupBox.setLayout(gridBox)
        self.groupBox.layout().setContentsMargins(0, 0, 0, 0)
        self.colorFilters.layout().setContentsMargins(0, 0, 0, 0)
        ContentLayout.addWidget(self.groupBox, 3, 1)

        self.checkIPDesc = QLabel(self.loc["tips"])
        self.checkIPDesc.setObjectName("checkIPDesc")
        self.checkIPDesc.setFixedWidth(250)
        self.checkIPDesc.setWordWrap(True)
        self.checkIPDesc.setAlignment(Qt.AlignCenter)
        ContentLayout.addWidget(self.checkIPDesc, 3, 2)
        self.groupBox2 = QWidget()
        gridBox2 = QGridLayout()
        self.filterLable = QLabel(self.loc["filter"])
        gridBox2.addWidget(self.filterLable, 0, 0, Qt.AlignTop)
        self.filterIP = QLineEdit(self)
        self.groupBox2.setFixedWidth(300)
        self.filterIP.textChanged.connect(self.filterIPandNames)

        self.InfoIP = QLabel()
        self.InfoIP.setObjectName("InfoIP")
        self.InfoCountry = QLabel()
        self.InfoCountry.setObjectName("InfoCountry")
        self.InfoFlag = QImage()
        self.InfoFlagLabel = QLabel()
        self.InfoFlagLabel.setObjectName("InfoFlag")
        self.InfoFlagLabel.setFixedSize(64, 64)
        gridBox2.addWidget(self.filterIP, 0, 1, Qt.AlignTop)
        gridBox2.addWidget(self.InfoIP, 1, 0, 1, 2)
        gridBox2.addWidget(self.InfoCountry, 2, 0, 1, 2, Qt.AlignTop)
        gridBox2.addWidget(self.InfoFlagLabel, 2, 1, Qt.AlignRight)
        self.groupBox2.setLayout(gridBox2)
        self.groupBox2.layout().setContentsMargins(0, 0, 0, 0)
        ContentLayout.addWidget(self.groupBox2, 3, 3)

        grid.addWidget(self.Content, 1, 1, 3, 3)

        self.timer = QTimer()
        self.timer.timeout.connect(self.UpdateLobby)
        self.timer.setSingleShot(False)
        self.timer.start(500)

        self.pingTimer = QTimer()
        self.pingTimer.timeout.connect(self.PingTimer)
        self.pingTimer.setSingleShot(False)
        self.pingTimer.start(5000)

        self.jsonPackets = self.openJSONPackets("log.json")
        self.jsonIPandNames = self.openJSONIPandNames("IPandNames.json")

        self.thread = SniffThread()
        self.thread.DataToUpdate.connect(self.AddNewItemToPacketListBox)
        self.thread.activeIP.connect(self.LaunchPing)
        self.thread.IPandESO.connect(self.AddNewItemToIPandNamesListBox)
        self.thread.speech.connect(self.playSpeech)
        self.thread.start()

        self.mainWindow.setFixedSize(1400, 580)

        self.setCursor(
            QtGui.QCursor(
                QtGui.QPixmap(self.getPath() + "Visuals/Cursor/AoE.png"), 0, 0
            )
        )
        self.mainWindow.layout().setContentsMargins(0, 0, 0, 0)
        self.mainWindow.layout().setSpacing(0)
        self.setFixedSize(1400, 580)
        self.setWindowTitle("ESO Packet Tracker, сopyright © 2019 by XaKOps")
        self.setWindowIcon(QIcon(self.getIconPath()))
        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def changeIPandNameFilter1(self, event):
        button = event.button()
        item = self.IPandNames.itemAt(event.x(), event.y())
        if item:
            if button == Qt.LeftButton:
                self.filterIP.setText(item.text().split(" : ")[0])
            if button == Qt.RightButton:

                thread = IPInfo(
                    ip=item.text().split(" : ")[0], name=item.text().split(" : ")[1]
                )
                thread.signals.infoSignal.connect(self.ActionsAfterIP)
                self.poolIPInfo.start(thread)

    def changeIPandNameFilter2(self, event):
        button = event.button()
        item = self.lobby.itemAt(event.x(), event.y())
        if item:
            if button == Qt.LeftButton:
                self.filterIP.setText(item.text().split(" : ")[0])
            if button == Qt.RightButton:

                thread = IPInfo(ip=item.text().split(" : ")[0], name="")
                thread.signals.infoSignal.connect(self.ActionsAfterIP)
                self.poolIPInfo.start(thread)

    def ActionsAfterIP(self, data):
        if data["Name"] != "":
            self.InfoIP.setText(data["IP"] + " : " + data["Name"])
        else:
            self.InfoIP.setText(data["IP"])
        if data["Country"] != self.loc["unknown"]:
            self.InfoCountry.setText(data["Country"] + ", " + data["City"])
        try:
            self.InfoFlag.loadFromData(data["Flag"])
            self.InfoFlagLabel.setPixmap(QtGui.QPixmap(self.InfoFlag))
        except:
            self.InfoFlagLabel.clear()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def soundsFilter(self):
        settings = QSettings("XaKOps", "ESO Packet Tracker")
        settings.setValue("box1", self.cb1.isChecked())
        settings.setValue("box2", self.cb2.isChecked())
        settings.setValue("box3", self.cb3.isChecked())
        settings.setValue("box4", self.cb4.isChecked())
        settings.setValue("box5", self.cb5.isChecked())
        settings.setValue("box6", self.cb6.isChecked())
        settings.setValue("box7", self.cb7.isChecked())
        settings.setValue("box8", self.cb8.isChecked())
        settings.setValue("box9", self.cb9.isChecked())

    def filterClicked(self):
        settings = QSettings("XaKOps", "ESO Packet Tracker")
        settings.setValue("box1", self.cb1.isChecked())
        settings.setValue("box2", self.cb2.isChecked())
        settings.setValue("box3", self.cb3.isChecked())
        settings.setValue("box4", self.cb4.isChecked())
        settings.setValue("box5", self.cb5.isChecked())
        settings.setValue("box6", self.cb6.isChecked())
        settings.setValue("box7", self.cb7.isChecked())
        settings.setValue("box8", self.cb8.isChecked())
        settings.setValue("box9", self.cb9.isChecked())
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
            self.jsonIPandNames = sorted(
                self.jsonIPandNames, key=lambda k: ipaddress.ip_address(k["IP"])
            )
            widgetItems = []
            for item in self.jsonIPandNames:
                widgetItems.append(item["IP"] + " : " + item["ESO"])
            self.IPandNames.clear()
            self.IPandNames.addItems(widgetItems)
            self.filterIPandNames()

    def UpdateIP(self, data):
        Item = next(
            (item for item in self.IPinLobby if item["IP"] == data["IP"]), False
        )
        if Item != False:
            Item["RTT"] = data["RTT"]
            # print(data["RTT"])

    def playSpeech(self, data):
        thread = Speech(
            speechType=data["speechType"],
            text=data["text"],
            who=data["who"],
            soundsFilter={
                "Notifications": self.cb6.isChecked(),
                "Connection": self.cb7.isChecked(),
                "Friends": self.cb8.isChecked(),
                "Messages": self.cb9.isChecked(),
            },
        )
        if data["speechType"] == "taunts":
            self.poolTaunts.start(thread)
        else:
            self.poolSpeech.start(thread)

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

    def PingTimer(self):
        for item in self.IPinLobby:
            thread = pingIP(item["IP"])
            thread.signals.playerinLobby.connect(self.UpdateIP)
            self.pool.start(thread)

    def UpdateLobby(self):
        self.IPinLobby = [
            IP
            for IP in self.IPinLobby
            if (datetime.now() - IP["LastUpdate"]).total_seconds() < 3
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
                buffer = j[-1024:]
                for item in buffer:
                    widgetItems.append(item["text"])
                self.w.addItems(widgetItems)
                for i in range(self.w.count()):
                    item = self.w.item(i)
                    if QColor(buffer[i]["color"].replace("black", clBlack)) == QColor(
                        clBlack
                    ):
                        item.setHidden(not (self.cb1.isChecked()))
                    if QColor(buffer[i]["color"]) == QColor(clViolet):
                        item.setHidden(not (self.cb2.isChecked()))
                    if QColor(buffer[i]["color"]) == QColor(clBlue):
                        item.setHidden(not (self.cb3.isChecked()))
                    if QColor(buffer[i]["color"]) == QColor(clGreen):
                        item.setHidden(not (self.cb4.isChecked()))
                    if QColor(buffer[i]["color"]) == QColor(clRed):
                        item.setHidden(not (self.cb5.isChecked()))

                    item.setForeground(
                        QColor(buffer[i]["color"].replace("black", clBlack))
                    )
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
                j = sorted(j, key=lambda k: ipaddress.ip_address(k["IP"]))
                widgetItems = []
                for item in j:
                    widgetItems.append(item["IP"] + " : " + item["ESO"])
                self.IPandNames.addItems(widgetItems)
                return j
            else:
                return []


if __name__ == "__main__":
    sys.stdout = open("stdout.txt", "a+")
    app = QApplication(sys.argv)

    mw = MainWindow()
    sys.exit(app.exec_())
