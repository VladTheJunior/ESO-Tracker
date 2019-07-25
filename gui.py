import json
import os
import os.path
import pkgutil
import sys
import ipaddress
import locale
import ctypes.wintypes
from datetime import datetime, timezone, timedelta
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, QRegExp
from PyQt5.QtGui import QRegExpValidator
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
from PyQt5.QtGui import QColor, QFont, QIcon, QImage, QPixmap
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QSizePolicy,
    QListView,
    QApplication,
    QCheckBox,
    QDesktopWidget,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QWidget,
    QButtonGroup,
    QRadioButton,
    QTabWidget,
    QFileDialog,
    QMessageBox,
    QGraphicsDropShadowEffect,
)

import localization
import Styles
from Constants import clBlack, clBlue, clGreen, clRed, clViolet, playerColors
from IPInfo import IPInfo
from PingIP import pingIP
from SniffThread import SniffThread
from Speech import Speech
from Models.LogListModel import LogListModel, LogFilterProxyModel
from Models.IPandESOListModel import IPandESOListModel, IPandESOFilterProxyModel
from Models.LobbyListModel import LobbyListModel, LobbyFilterProxyModel
from RecordParser import RecordGame
from Models.PlayerActionsListModel import (
    PlayerActionsListModel,
    PlayerActionsProxyModel,
)
from Models.DeckListModel import DeckListModel


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
        self.Scrolled = True
        self.jsonPackets = []
        self.jsonIPandNames = []
        self.IPinLobby = []
        self.pool = QThreadPool()
        self.poolIPInfo = QThreadPool()
        self.RecordedGamePool = QThreadPool()
        self.poolTaunts = QThreadPool()
        self.poolSpeech = QThreadPool()
        self.poolSpeech.setMaxThreadCount(1)
        self.poolIPInfo.setMaxThreadCount(8)

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
        self.TopLeft.mouseMoveEvent = self.mMoveEvent
        self.TopLeft.mousePressEvent = self.mPressEvent
        grid.addWidget(self.TopLeft, 0, 0)

        self.Left = QWidget()
        self.Left.setFixedSize(24, 570)
        self.Left.setObjectName("Left")
        self.Left.mouseMoveEvent = self.mMoveEvent
        self.Left.mousePressEvent = self.mPressEvent
        grid.addWidget(self.Left, 2, 0)

        self.TopLeftBottom = QWidget()
        self.TopLeftBottom.setFixedSize(24, 82)
        self.TopLeftBottom.setObjectName("TopLeftBottom")
        self.TopLeftBottom.mouseMoveEvent = self.mMoveEvent
        self.TopLeftBottom.mousePressEvent = self.mPressEvent

        grid.addWidget(self.TopLeftBottom, 1, 0)

        self.BottomLeftTop = QWidget()
        self.BottomLeftTop.setFixedSize(24, 82)
        self.BottomLeftTop.setObjectName("BottomLeftTop")
        self.BottomLeftTop.mouseMoveEvent = self.mMoveEvent
        self.BottomLeftTop.mousePressEvent = self.mPressEvent

        grid.addWidget(self.BottomLeftTop, 3, 0, Qt.AlignBottom)

        self.BottomLeft = QWidget()
        self.BottomLeft.setObjectName("BottomLeft")
        self.BottomLeft.setFixedSize(24, 24)
        self.BottomLeft.mouseMoveEvent = self.mMoveEvent
        self.BottomLeft.mousePressEvent = self.mPressEvent
        grid.addWidget(self.BottomLeft, 4, 0)

        self.BottomLeftRight = QWidget()
        self.BottomLeftRight.setObjectName("BottomLeftRight")
        self.BottomLeftRight.setFixedSize(82, 24)
        self.BottomLeftRight.mouseMoveEvent = self.mMoveEvent
        self.BottomLeftRight.mousePressEvent = self.mPressEvent
        grid.addWidget(self.BottomLeftRight, 4, 1)

        self.Bottom = QWidget()
        self.Bottom.setObjectName("Bottom")
        self.Bottom.setFixedSize(994, 24)
        self.Bottom.mouseMoveEvent = self.mMoveEvent
        self.Bottom.mousePressEvent = self.mPressEvent
        grid.addWidget(self.Bottom, 4, 2)

        self.Right = QWidget()
        self.Right.setObjectName("Right")
        self.Right.setFixedSize(24, 570)
        self.Right.mouseMoveEvent = self.mMoveEvent
        self.Right.mousePressEvent = self.mPressEvent
        grid.addWidget(self.Right, 2, 4)

        self.BottomRightLeft = QWidget()
        self.BottomRightLeft.setObjectName("BottomRightLeft")
        self.BottomRightLeft.setFixedSize(82, 24)
        self.BottomRightLeft.mouseMoveEvent = self.mMoveEvent
        self.BottomRightLeft.mousePressEvent = self.mPressEvent
        grid.addWidget(self.BottomRightLeft, 4, 3)

        self.BottomRight = QWidget()
        self.BottomRight.setObjectName("BottomRight")
        self.BottomRight.setFixedSize(24, 24)
        self.BottomRight.mouseMoveEvent = self.mMoveEvent
        self.BottomRight.mousePressEvent = self.mPressEvent
        grid.addWidget(self.BottomRight, 4, 4)

        self.BottomRightTop = QWidget()
        self.BottomRightTop.setObjectName("BottomRightTop")
        self.BottomRightTop.setFixedSize(24, 82)
        self.BottomRightTop.mouseMoveEvent = self.mMoveEvent
        self.BottomRightTop.mousePressEvent = self.mPressEvent
        grid.addWidget(self.BottomRightTop, 3, 4)

        self.Top = QWidget()
        self.Top.setObjectName("Top")
        self.Top.mouseMoveEvent = self.mMoveEvent
        self.Top.mousePressEvent = self.mPressEvent
        self.Top.setFixedSize(1032, 24)
        grid.addWidget(self.Top, 0, 2)

        self.TopRight = QPushButton()
        self.TopRight.setObjectName("TopRight")
        self.TopRight.setFixedSize(24, 24)
        self.TopRight.clicked.connect(self.close)
        grid.addWidget(self.TopRight, 0, 4)

        self.TopRightLeft = QWidget()
        self.TopRightLeft.setObjectName("TopRightLeft")
        self.TopRightLeft.setFixedSize(82, 24)
        self.TopRightLeft.mouseMoveEvent = self.mMoveEvent
        self.TopRightLeft.mousePressEvent = self.mPressEvent
        grid.addWidget(self.TopRightLeft, 0, 3)

        self.TopRightBottom = QWidget()
        self.TopRightBottom.setObjectName("TopRightBottom")
        self.TopRightBottom.setFixedSize(24, 82)
        self.TopRightBottom.mouseMoveEvent = self.mMoveEvent
        self.TopRightBottom.mousePressEvent = self.mPressEvent
        grid.addWidget(self.TopRightBottom, 1, 4)

        self.TopLeftRight = QWidget()
        self.TopLeftRight.setObjectName("TopLeftRight")
        self.TopLeftRight.mouseMoveEvent = self.mMoveEvent
        self.TopLeftRight.mousePressEvent = self.mPressEvent
        self.TopLeftRight.setFixedSize(82, 24)

        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setColor(QColor("#000000"))
        self.shadow.setOffset(2, 2)
        self.shadow.setBlurRadius(0)

        self.Title = QLabel("ESO Tracker")
        self.Title.setObjectName("Title")
        self.Title.setGraphicsEffect(self.shadow)
        self.Title.setAlignment(Qt.AlignCenter)
        self.Title.setFixedSize(226, 24)
        self.Title.mouseMoveEvent = self.mMoveEvent
        self.Title.mousePressEvent = self.mPressEvent

        self.TitleBkg = QWidget()
        self.TitleBkg.setFixedSize(226, 24)
        self.TitleBkg.setObjectName("TitleBkg")
        self.TitleBkg.mouseMoveEvent = self.mMoveEvent
        self.TitleBkg.mousePressEvent = self.mPressEvent
        grid.addWidget(self.TitleBkg, 0, 2)
        grid.addWidget(self.Title, 0, 2)

        grid.addWidget(self.TopLeftRight, 0, 1)

        self.Content = QWidget()
        ContentLayout = QGridLayout()
        self.Content.setLayout(ContentLayout)
        self.Content.layout().setSpacing(0)
        MenuLayout = QVBoxLayout()
        MenuLayout.setSpacing(5)
        MenuLayout.addStretch()
        Menu = QButtonGroup()

        self.MenuItem1 = QPushButton()
        self.MenuItem1.setObjectName("MenuItem")

        self.MenuItem1.setCheckable(True)
        self.MenuItem1.setAutoExclusive(True)
        self.MenuItem1.setChecked(True)
        self.MenuItem1.clicked.connect(self.MenuItem1Click)
        self.MenuItem1.setText(self.loc["plogs"])
        self.MenuItem1.setFixedSize(192, 32)
        Menu.addButton(self.MenuItem1)
        MenuLayout.addWidget(self.MenuItem1)
        self.MenuItem2 = QPushButton()

        self.MenuItem2.setObjectName("MenuItem")
        self.MenuItem2.setText("IP Checker")
        self.MenuItem2.clicked.connect(self.MenuItem2Click)
        self.MenuItem2.setCheckable(True)
        self.MenuItem2.setAutoExclusive(True)
        self.MenuItem2.setFixedSize(192, 32)
        Menu.addButton(self.MenuItem2)
        MenuLayout.addWidget(self.MenuItem2)
        self.MenuItem3 = QPushButton()
        self.MenuItem3.setObjectName("MenuItem")
        self.MenuItem3.setText(self.loc["settings"])
        self.MenuItem3.clicked.connect(self.MenuItem3Click)
        self.MenuItem3.setFixedSize(192, 32)
        self.MenuItem3.setCheckable(True)
        self.MenuItem3.setAutoExclusive(True)
        Menu.addButton(self.MenuItem3)

        self.MenuItem4 = QPushButton()
        self.MenuItem4.setObjectName("MenuItem")
        self.MenuItem4.setText(self.loc["RecordedGame"])
        self.MenuItem4.setFixedSize(192, 32)
        self.MenuItem4.clicked.connect(self.MenuItem4Click)
        self.MenuItem4.setCheckable(True)
        self.MenuItem4.setAutoExclusive(True)
        Menu.addButton(self.MenuItem4)
        MenuLayout.addWidget(self.MenuItem4)
        MenuLayout.addWidget(self.MenuItem3)
        MenuLayout.addStretch()

        self.Menu = QWidget()
        self.Menu.setLayout(MenuLayout)
        ContentLayout.addWidget(self.Menu, 0, 0, Qt.AlignLeft)
        self.Menu.layout().setContentsMargins(0, 0, 0, 0)

        self.MenuContent = QWidget()
        self.MenuContent.setObjectName("MenuContent")
        MenuContentLayout = QGridLayout()

        self.BTopLeft = QWidget()

        self.BTopLeft.setObjectName("BTopLeft")
        self.BTopLeft.setFixedSize(16, 16)
        MenuContentLayout.addWidget(self.BTopLeft, 0, 0)

        self.BLeft = QWidget()
        self.BLeft.setFixedSize(14, 666)
        self.BLeft.setObjectName("BLeft")
        MenuContentLayout.addWidget(self.BLeft, 1, 0)

        self.BBottomLeft = QWidget()
        self.BBottomLeft.setObjectName("BBottomLeft")
        self.BBottomLeft.setFixedSize(16, 16)
        MenuContentLayout.addWidget(self.BBottomLeft, 2, 0, Qt.AlignBottom)

        self.BBottom = QWidget()
        self.BBottom.setObjectName("BBottom")
        self.BBottom.setFixedSize(864, 14)
        MenuContentLayout.addWidget(self.BBottom, 2, 1, Qt.AlignBottom)

        self.BRight = QWidget()
        self.BRight.setObjectName("BRight")
        self.BRight.setFixedSize(14, 666)
        MenuContentLayout.addWidget(self.BRight, 1, 2, Qt.AlignRight)

        self.BBottomRight = QWidget()
        self.BBottomRight.setObjectName("BBottomRight")
        self.BBottomRight.setFixedSize(16, 16)
        MenuContentLayout.addWidget(self.BBottomRight, 2, 2)

        self.BTop = QWidget()
        self.BTop.setObjectName("BTop")
        self.BTop.setFixedSize(864, 14)
        MenuContentLayout.addWidget(self.BTop, 0, 1, Qt.AlignTop)

        self.BTopRight = QWidget()
        self.BTopRight.setObjectName("BTopRight")
        self.BTopRight.setFixedSize(16, 16)
        MenuContentLayout.addWidget(self.BTopRight, 0, 2)

        self.MenuContent.setLayout(MenuContentLayout)
        ContentLayout.addWidget(self.MenuContent, 0, 1, Qt.AlignLeft)
        self.MenuContent.layout().setSpacing(0)
        self.MenuContent.layout().setContentsMargins(0, 0, 0, 0)

        self.ESOPacketsLog = QWidget()
        ESOPacketsLogLayout = QGridLayout()

        self.l = QLabel(self.loc["plogs"])
        self.l.setObjectName("TextBlock")
        self.l.setFixedSize(256, 32)
        self.l.setAlignment(Qt.AlignCenter)
        ESOPacketsLogLayout.addWidget(self.l, 0, 0, 1, 2, Qt.AlignCenter)

        self.filterLable = QLabel(self.loc["filter"])

        ESOPacketsLogLayout.addWidget(self.filterLable, 2, 0)

        self.filter = QLineEdit(self)
        self.filter.textChanged.connect(self.filterClicked)
        ESOPacketsLogLayout.addWidget(self.filter, 2, 1)

        self.ESOPacketsLog.setLayout(ESOPacketsLogLayout)

        MenuContentLayout.addWidget(self.ESOPacketsLog, 1, 1)

        self.IPChecker = QWidget()
        IPCheckerLayout = QGridLayout()

        self.lobby = QListView()
        self.lobby.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.lobby.mousePressEvent = self.changeIPandNameFilter2
        self.lobbyModel = LobbyListModel(self.IPinLobby)
        self.lobbyProxyMidel = LobbyFilterProxyModel(self.lobbyModel)
        self.lobby.setModel(self.lobbyProxyMidel)
        self.lobby.setFont(QFont("Consolas", 11, weight=QFont.Bold))
        IPCheckerLayout.addWidget(self.lobby, 1, 0)

        self.filterLable = QLabel(self.loc["filter"])
        IPCheckerLayout.addWidget(self.filterLable, 2, 1)

        self.AddIP = QLineEdit()
        self.AddName = QLineEdit()
        self.AddButton = QPushButton()
        self.AddButton.setObjectName("Add")
        self.AddButton.setFixedSize(32, 32)
        self.AddButton.clicked.connect(self.AddManualIP)
        self.AddIP.textChanged.connect(self.filterIPandNames)
        self.AddName.textChanged.connect(self.filterIPandNames)
        self.AddIP.setPlaceholderText(self.loc["IP Address"])
        self.AddName.setPlaceholderText(self.loc["ESO Name"])
        ipRange = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        ipRegex = QRegExp(
            "^" + ipRange + "\\." + ipRange + "\\." + ipRange + "\\." + ipRange + "$"
        )
        ipValidator = QRegExpValidator(ipRegex, self)
        self.AddIP.setValidator(ipValidator)
        ipValidator = QRegExpValidator(ipRegex, self)

        IPCheckerLayout.addWidget(self.AddIP, 2, 2)
        IPCheckerLayout.addWidget(self.AddName, 2, 3)
        IPCheckerLayout.addWidget(self.AddButton, 2, 4)

        IPCheckerLayout.setColumnStretch(0, 3)

        IPCheckerLayout.setColumnStretch(3, 2)

        self.l2 = QLabel(self.loc["playersinlobby"])
        self.l2.setObjectName("TextBlock")
        self.l2.setFixedSize(256, 32)
        self.l2.setAlignment(Qt.AlignCenter)
        IPCheckerLayout.addWidget(self.l2, 0, 0, Qt.AlignCenter)

        self.l3 = QLabel(self.loc["ipandeso"])
        self.l3.setObjectName("TextBlock")
        self.l3.setFixedSize(256, 32)
        self.l3.setAlignment(Qt.AlignCenter)
        IPCheckerLayout.addWidget(self.l3, 0, 1, 1, 4, Qt.AlignCenter)

        self.IPChecker.setLayout(IPCheckerLayout)
        self.IPChecker.setVisible(False)
        MenuContentLayout.addWidget(self.IPChecker, 1, 1)
        self.Settings = QWidget()

        SettingsLayout = QGridLayout()

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
        self.ColorSetting = QWidget()
        ColorsLayout = QVBoxLayout()

        self.Colors = QLabel(self.loc["Colors"])
        self.Colors.setObjectName("TextBlock")
        self.Colors.setFixedSize(256, 32)
        self.Colors.setAlignment(Qt.AlignCenter)
        SettingsLayout.addWidget(self.Colors, 0, 0, Qt.AlignHCenter)

        self.cb1 = QCheckBox(self.loc["black"])
        self.cb1.setObjectName("standardCheckBox")
        self.cb1.setChecked(cs1)
        self.cb1.clicked.connect(self.filterClicked)
        ColorsLayout.addWidget(self.cb1)

        self.cb2 = QCheckBox(self.loc["violet"])
        self.cb2.setObjectName("standardCheckBox")
        self.cb2.setChecked(cs2)

        self.cb2.clicked.connect(self.filterClicked)
        ColorsLayout.addWidget(self.cb2)

        self.cb3 = QCheckBox(self.loc["blue"])
        self.cb3.setObjectName("standardCheckBox")
        self.cb3.setChecked(cs3)
        self.cb3.clicked.connect(self.filterClicked)
        ColorsLayout.addWidget(self.cb3)

        self.cb4 = QCheckBox(self.loc["green"])
        self.cb4.setObjectName("standardCheckBox")
        self.cb4.setChecked(cs4)

        self.cb4.clicked.connect(self.filterClicked)
        ColorsLayout.addWidget(self.cb4)

        self.cb5 = QCheckBox(self.loc["red"])
        self.cb5.setObjectName("standardCheckBox")

        self.cb5.setChecked(cs5)
        self.cb5.clicked.connect(self.filterClicked)

        ColorsLayout.addWidget(self.cb5)
        self.ColorSetting.setLayout(ColorsLayout)
        SettingsLayout.addWidget(self.ColorSetting, 1, 0)

        self.SoundSetting = QWidget()
        SoundSettingLayout = QVBoxLayout()
        self.Sounds = QLabel(self.loc["sounds"])
        self.Sounds.setObjectName("TextBlock")
        self.Sounds.setFixedSize(256, 32)
        self.Sounds.setAlignment(Qt.AlignCenter)
        SettingsLayout.addWidget(self.Sounds, 2, 0, Qt.AlignHCenter)

        self.cb6 = QCheckBox(self.loc["Notifications"])
        self.cb6.setObjectName("standardCheckBox")
        self.cb6.setChecked(cs6)
        self.cb6.clicked.connect(self.soundsFilter)
        SoundSettingLayout.addWidget(self.cb6)

        self.cb7 = QCheckBox(self.loc["connection"])
        self.cb7.setObjectName("standardCheckBox")
        self.cb7.setChecked(cs7)
        self.cb7.clicked.connect(self.soundsFilter)
        SoundSettingLayout.addWidget(self.cb7)

        self.cb8 = QCheckBox(self.loc["Friends"])
        self.cb8.setObjectName("standardCheckBox")
        self.cb8.setChecked(cs8)
        self.cb8.clicked.connect(self.soundsFilter)
        SoundSettingLayout.addWidget(self.cb8)

        self.cb9 = QCheckBox(self.loc["Messages"])
        self.cb9.setObjectName("standardCheckBox")
        self.cb9.setChecked(cs9)
        self.cb9.clicked.connect(self.soundsFilter)
        SoundSettingLayout.addWidget(self.cb9)

        self.SoundSetting.setLayout(SoundSettingLayout)
        SettingsLayout.addWidget(self.SoundSetting, 3, 0)
        SettingsLayout.setRowStretch(4, 1)
        self.Settings.setLayout(SettingsLayout)
        self.Settings.layout().setSpacing(0)
        self.Settings.setVisible(False)
        MenuContentLayout.addWidget(self.Settings, 1, 1)

        self.RecordedGame = QWidget()
        RecordedGameLayout = QGridLayout()

        self.RecordTabs = QTabWidget()
        self.GameInfo = QWidget()
        self.GameInfo.setObjectName("TabPanel")
        GameInfoLayout = QGridLayout()

        self.gameName = QLabel()
        self.gameName.setObjectName("GameName")
        self.exeVersion = QLabel()
        self.exeVersion.setObjectName("GameInfo")
        self.Map = QLabel()
        self.Map.setObjectName("MapName")
        self.Mode = QLabel()
        self.Mode.setObjectName("GameInfo")
        self.Duration = QLabel()
        self.Duration.setObjectName("GameInfo")

        self.Team1 = QWidget()
        self.Team2 = QWidget()

        self.MapIcon = QLabel()

        GameInfoLayout.addWidget(self.gameName, 0, 0, 2, 2, Qt.AlignCenter)
        GameInfoLayout.addWidget(self.Map, 2, 0, Qt.AlignLeft)
        GameInfoLayout.addWidget(self.MapIcon, 3, 0, 5, 1, Qt.AlignLeft)
        GameInfoLayout.addWidget(self.Mode, 4, 1)
        GameInfoLayout.addWidget(self.exeVersion, 5, 1)

        GameInfoLayout.addWidget(self.Duration, 6, 1)
        GameInfoLayout.addWidget(self.Team1, 8, 0)
        GameInfoLayout.addWidget(self.Team2, 8, 1)

        GameInfoLayout.setColumnStretch(0, 1)
        GameInfoLayout.setColumnStretch(1, 1)

        GameInfoLayout.setRowStretch(1, 1)
        GameInfoLayout.setRowStretch(3, 1)
        GameInfoLayout.setRowStretch(7, 1)

        self.GameInfo.setLayout(GameInfoLayout)
        # self.GameInfo.layout().setContentsMargins(0, 0, 0, 0)
        self.RecordTabs.addTab(self.GameInfo, self.loc["GameInfo"])

        self.GameDecks = QWidget()
        self.GameDecks.setObjectName("TabPanel")
        GameDecksLayout = QGridLayout()

        self.Decks = QListView()
        self.Decks.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.Decks.setFont(QFont("Consolas", 11, weight=QFont.Bold))
        GameDecksLayout.addWidget(self.Decks, 0, 0)

        self.GameDecks.setLayout(GameDecksLayout)
        self.GameDecks.layout().setContentsMargins(0, 0, 0, 0)
        self.RecordTabs.addTab(self.GameDecks, self.loc["Decks"])

        self.GameActions = QWidget()
        self.GameActions.setObjectName("TabPanel")
        GameActionsLayout = QGridLayout()
        self.GameActions.setLayout(GameActionsLayout)

        self.PlayerActions = QListView()
        self.PlayerActions.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.PlayerActions.setFont(QFont("Consolas", 11, weight=QFont.Bold))
        GameActionsLayout.addWidget(self.PlayerActions, 0, 0, 1, 8)

        self.player1Color = QCheckBox()
        self.player1Color.setChecked(True)

        self.player1Color.setObjectName("Player1Color")
        self.player1Color.clicked.connect(self.filterActionsClicked)
        self.player2Color = QCheckBox()
        self.player2Color.setChecked(True)
        self.player2Color.setObjectName("Player2Color")
        self.player2Color.clicked.connect(self.filterActionsClicked)
        self.player3Color = QCheckBox()
        self.player3Color.setChecked(True)
        self.player3Color.setObjectName("Player3Color")
        self.player3Color.clicked.connect(self.filterActionsClicked)
        self.player4Color = QCheckBox()
        self.player4Color.setChecked(True)
        self.player4Color.setObjectName("Player4Color")
        self.player4Color.clicked.connect(self.filterActionsClicked)
        self.player5Color = QCheckBox()
        self.player5Color.setChecked(True)
        self.player5Color.setObjectName("Player5Color")
        self.player5Color.clicked.connect(self.filterActionsClicked)
        self.player6Color = QCheckBox()
        self.player6Color.setChecked(True)
        self.player6Color.setObjectName("Player6Color")
        self.player6Color.clicked.connect(self.filterActionsClicked)
        self.player7Color = QCheckBox()
        self.player7Color.setChecked(True)
        self.player7Color.setObjectName("Player7Color")
        self.player7Color.clicked.connect(self.filterActionsClicked)
        self.player8Color = QCheckBox()
        self.player8Color.setChecked(True)
        self.player8Color.setObjectName("Player8Color")
        self.player8Color.clicked.connect(self.filterActionsClicked)

        self.cbBuild = QCheckBox(self.loc["cbbuild"])
        self.cbBuild.setObjectName("standardCheckBoxW")
        self.cbBuild.setChecked(False)
        self.cbBuild.clicked.connect(self.filterActionsClicked)

        self.cbTrain = QCheckBox(self.loc["cbtrain"])
        self.cbTrain.setObjectName("standardCheckBoxW")
        self.cbTrain.setChecked(False)
        self.cbTrain.clicked.connect(self.filterActionsClicked)

        self.cbShipment = QCheckBox(self.loc["cbshipment"])
        self.cbShipment.setObjectName("standardCheckBoxW")
        self.cbShipment.setChecked(True)
        self.cbShipment.clicked.connect(self.filterActionsClicked)

        self.cbSpawnUnit = QCheckBox(self.loc["cbspawn_unit"])
        self.cbSpawnUnit.setObjectName("standardCheckBoxW")
        self.cbSpawnUnit.setChecked(True)
        self.cbSpawnUnit.clicked.connect(self.filterActionsClicked)

        self.cbResearchTech = QCheckBox(self.loc["cbresearch_tech1"])
        self.cbResearchTech.setObjectName("standardCheckBoxW")
        self.cbResearchTech.setChecked(True)
        self.cbResearchTech.clicked.connect(self.filterActionsClicked)

        self.cbResearchCheatTech = QCheckBox(self.loc["cbresearch_tech23"])
        self.cbResearchCheatTech.setObjectName("standardCheckBoxW")
        self.cbResearchCheatTech.setChecked(True)
        self.cbResearchCheatTech.clicked.connect(self.filterActionsClicked)

        self.cbPickDeck = QCheckBox(self.loc["cbpick_deck"])
        self.cbPickDeck.setObjectName("standardCheckBoxW")
        self.cbPickDeck.setChecked(True)
        self.cbPickDeck.clicked.connect(self.filterActionsClicked)

        self.cbResigned = QCheckBox(self.loc["cbresigned"])
        self.cbResigned.setObjectName("standardCheckBoxW")
        self.cbResigned.setChecked(True)
        self.cbResigned.clicked.connect(self.filterActionsClicked)

        self.l5 = QLabel(self.loc["playerscolors"])
        self.l5.setObjectName("MapName")
        self.l6 = QLabel(self.loc["playersaction"])
        self.l6.setObjectName("MapName")

        GameActionsLayout.addWidget(self.l6, 1, 0, 1, 8)

        GameActionsLayout.addWidget(self.cbBuild, 2, 0, 1, 2)
        GameActionsLayout.addWidget(self.cbPickDeck, 2, 2, 1, 2)
        GameActionsLayout.addWidget(self.cbResearchCheatTech, 2, 4, 1, 2)
        GameActionsLayout.addWidget(self.cbResigned, 2, 6, 1, 2)

        GameActionsLayout.addWidget(self.cbResearchTech, 3, 0, 1, 2)
        GameActionsLayout.addWidget(self.cbShipment, 3, 2, 1, 2)
        GameActionsLayout.addWidget(self.cbSpawnUnit, 3, 4, 1, 2)
        GameActionsLayout.addWidget(self.cbTrain, 3, 6, 1, 2)

        GameActionsLayout.addWidget(self.l5, 4, 0, 1, 8)

        GameActionsLayout.addWidget(self.player1Color, 5, 0, Qt.AlignCenter)
        GameActionsLayout.addWidget(self.player2Color, 5, 1, Qt.AlignCenter)
        GameActionsLayout.addWidget(self.player3Color, 5, 2, Qt.AlignCenter)
        GameActionsLayout.addWidget(self.player4Color, 5, 3, Qt.AlignCenter)
        GameActionsLayout.addWidget(self.player5Color, 5, 4, Qt.AlignCenter)
        GameActionsLayout.addWidget(self.player6Color, 5, 5, Qt.AlignCenter)
        GameActionsLayout.addWidget(self.player7Color, 5, 6, Qt.AlignCenter)
        GameActionsLayout.addWidget(self.player8Color, 5, 7, Qt.AlignCenter)

        self.GameActions.layout().setContentsMargins(0, 0, 0, 0)
        self.RecordTabs.addTab(self.GameActions, self.loc["GameActions"])

        self.l4 = QLabel()
        self.l4.setText(self.loc["RecordedGame"])
        self.l4.setObjectName("TextBlock")
        self.l4.setFixedSize(256, 32)
        self.l4.setAlignment(Qt.AlignCenter)
        RecordedGameLayout.addWidget(self.l4, 0, 0, 1, 2, Qt.AlignCenter)

        RecordedGameLayout.addWidget(self.RecordTabs, 1, 0, 1, 2)

        self.ParseButton = QPushButton()
        self.ParseButton.setObjectName("Button")
        self.ParseButton.setFixedSize(192, 32)
        self.ParseButton.setText(self.loc["openfile"])
        self.ParseButton.clicked.connect(self.OpenAndParse)

        RecordedGameLayout.addWidget(self.ParseButton, 2, 1)

        self.openlabel = QLabel()
        self.openlabel.setText(self.loc["openlabel"])

        RecordedGameLayout.addWidget(self.openlabel, 2, 0)

        self.RecordedGame.setLayout(RecordedGameLayout)

        self.RecordedGame.setVisible(False)
        MenuContentLayout.addWidget(self.RecordedGame, 1, 1)

        grid.addWidget(self.Content, 1, 1, 3, 3)

        self.pingTimer = QTimer()
        self.pingTimer.timeout.connect(self.PingTimer)
        self.pingTimer.setSingleShot(False)
        self.pingTimer.start(10000)

        self.filterLobbyTimer = QTimer()
        self.filterLobbyTimer.timeout.connect(self.ApplyLobbyFilter)
        self.filterLobbyTimer.setSingleShot(False)
        self.filterLobbyTimer.start(1000)

        self.jsonPackets = self.openJSONPackets("log.json")
        self.jsonIPandNames = self.openJSONIPandNames("IPandNames.json")

        FilterPattern = {"colors": [], "text": ""}
        if self.cb1.isChecked():
            FilterPattern["colors"].append(QColor(clBlack))
        if self.cb2.isChecked():
            FilterPattern["colors"].append(QColor(clViolet))
        if self.cb3.isChecked():
            FilterPattern["colors"].append(QColor(clBlue))
        if self.cb4.isChecked():
            FilterPattern["colors"].append(QColor(clGreen))
        if self.cb5.isChecked():
            FilterPattern["colors"].append(QColor(clRed))        
        self.logs = QListView()
        self.logs.setFont(QFont("Consolas", 11, weight=QFont.Bold))
        self.logsModel = LogListModel(self.jsonPackets)
        self.logs.verticalScrollBar().valueChanged.connect(self.scrolled)
        self.logs.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.logsFilterModel = LogFilterProxyModel(FilterPattern, self.logsModel)
        self.logs.setModel(self.logsFilterModel)
        ESOPacketsLogLayout.addWidget(self.logs, 1, 0, 1, 2)

        self.IPandNames = QListView()
        self.IPandNames.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.IPandNames.mousePressEvent = self.changeIPandNameFilter1
        self.IPandNames.setFont(QFont("Consolas", 11, weight=QFont.Bold))
        self.IPandNamesModel = IPandESOListModel(self.jsonIPandNames)
        self.IPandNamesFilterModel = IPandESOFilterProxyModel(
            {"IP": "", "ESO": ""}, self.IPandNamesModel
        )
        self.IPandNames.setModel(self.IPandNamesFilterModel)
        self.IPandNamesFilterModel.sort(0, Qt.AscendingOrder)

        IPCheckerLayout.addWidget(self.IPandNames, 1, 1, 1, 4)

        try:
            self.thread = SniffThread()
            self.thread.DataToUpdate.connect(self.AddNewItemToPacketListBox)
            self.thread.activeIP.connect(self.LaunchPing)
            self.thread.IPandESO.connect(self.AddNewItemToIPandNamesListBox)
            self.thread.speech.connect(self.playSpeech)
            self.thread.start()
        except:
            pass

        self.mainWindow.setFixedSize(1124, 750)

        self.setCursor(
            QtGui.QCursor(
                QtGui.QPixmap(self.getPath() + "Visuals/Cursor/AoE.png"), 0, 0
            )
        )
        self.mainWindow.layout().setContentsMargins(0, 0, 0, 0)
        self.mainWindow.layout().setSpacing(0)
        self.setFixedSize(1124, 750)
        self.setWindowTitle("ESO Tracker, сopyright © 2019 by XaKOps")
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
        item = self.IPandNames.indexAt(event.pos())
        if item.isValid():
            if button == Qt.LeftButton:
                data = item.data(Qt.UserRole)
                self.AddIP.setText(data["IP"])
                self.AddName.setText(data["ESO"])

    def changeIPandNameFilter2(self, event):
        button = event.button()
        item = self.lobby.indexAt(event.pos())
        if item.isValid():
            if button == Qt.LeftButton:
                self.AddIP.setText(item.data().split(" : ")[0])
                self.AddName.setText("")

    def ActionsAfterIP(self, data):
        if data["Name"] == "":
            Item = next(
                (item for item in self.IPinLobby if item["IP"] == data["IP"]), False
            )
            if Item != False:
                Item["IPInfo"] = data
        else:
            Item = next(
                (
                    item
                    for item in self.jsonIPandNames
                    if item["IP"] == data["IP"] and item["ESO"] == data["Name"]
                ),
                False,
            )
            if Item != False:
                Item["IPInfo"] = data

    def mPressEvent(self, event):
        self.oldPos = event.globalPos()

    def mMoveEvent(self, event):
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

    def filterActionsClicked(self):

        FilterPattern = {"colors": [], "actions": []}
        if self.player1Color.isChecked():
            FilterPattern["colors"].append(playerColors[0])
        if self.player2Color.isChecked():
            FilterPattern["colors"].append(playerColors[1])
        if self.player3Color.isChecked():
            FilterPattern["colors"].append(playerColors[2])
        if self.player4Color.isChecked():
            FilterPattern["colors"].append(playerColors[3])
        if self.player5Color.isChecked():
            FilterPattern["colors"].append(playerColors[4])
        if self.player6Color.isChecked():
            FilterPattern["colors"].append(playerColors[5])
        if self.player7Color.isChecked():
            FilterPattern["colors"].append(playerColors[6])
        if self.player8Color.isChecked():
            FilterPattern["colors"].append(playerColors[7])

        if self.cbBuild.isChecked():
            FilterPattern["actions"].append("build")
        if self.cbPickDeck.isChecked():
            FilterPattern["actions"].append("pick_deck")
        if self.cbResearchCheatTech.isChecked():
            FilterPattern["actions"].append("research_tech2")
            FilterPattern["actions"].append("research_tech3")
        if self.cbResearchTech.isChecked():
            FilterPattern["actions"].append("research_tech1")
        if self.cbResigned.isChecked():
            FilterPattern["actions"].append("resigned")
        if self.cbShipment.isChecked():
            FilterPattern["actions"].append("shipment")
        if self.cbSpawnUnit.isChecked():
            FilterPattern["actions"].append("spawn_unit")
        if self.cbTrain.isChecked():
            FilterPattern["actions"].append("train")

        self.PlayerActionsFilterModel.setFilterPattern(FilterPattern)

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

        FilterPattern = {"colors": [], "text": ""}
        if self.cb1.isChecked():
            FilterPattern["colors"].append(QColor(clBlack))
        if self.cb2.isChecked():
            FilterPattern["colors"].append(QColor(clViolet))
        if self.cb3.isChecked():
            FilterPattern["colors"].append(QColor(clBlue))
        if self.cb4.isChecked():
            FilterPattern["colors"].append(QColor(clGreen))
        if self.cb5.isChecked():
            FilterPattern["colors"].append(QColor(clRed))

        FilterPattern["text"] = self.filter.text()
        self.logsFilterModel.setFilterPattern(FilterPattern)
        if self.Scrolled:
            self.logs.scrollToBottom()

    def scrolled(self, value):
        self.Scrolled = value == self.logs.verticalScrollBar().maximum()


    def AddManualIP(self):
        if self.AddIP.text() != "" and self.AddName.text() != "":
            self.AddNewItemToIPandNamesListBox({"IP": self.AddIP.text(), "ESO": self.AddName.text()})        

    def filterIPandNames(self):
        self.IPandNamesFilterModel.setFilterPattern({"IP": self.AddIP.text(), "ESO": self.AddName.text()})       

    def AddNewItemToPacketListBox(self, data):
        self.logsModel.insertRecord({"text": data[0], "color": data[1]})
        self.filterClicked()

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
            self.IPandNamesModel.insertRecord({"IP": data["IP"], "ESO": data["ESO"]})
            thread = IPInfo(ip=data["IP"], name=data["ESO"])
            thread.signals.infoSignal.connect(self.ActionsAfterIP)
            self.poolIPInfo.start(thread)
            self.filterIPandNames()

    def UpdateIP(self, data):
        Item = next(
            (item for item in self.IPinLobby if item["IP"] == data["IP"]), False
        )
        if Item != False:
            Item["RTT"] = data["RTT"]

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
            self.lobbyModel.insertRecord(
                {
                    "IP": data,
                    "LastUpdate": datetime.now(),
                    "RTT": "N/A",
                    "nicknames": [],
                }
            )
        else:
            Item["LastUpdate"] = datetime.now()

    def ApplyLobbyFilter(self):
        self.lobbyProxyMidel.setFilterPattern(datetime.now())

    def PingTimer(self):
        for item in self.IPinLobby:
            if (datetime.now() - item["LastUpdate"]).total_seconds() < 3:
                thread = pingIP(item["IP"])
                thread.signals.playerinLobby.connect(self.UpdateIP)
                self.pool.start(thread)
                if "IPInfo" not in item or (
                    "IPInfo" in item and "ISP" not in item["IPInfo"]
                ):
                    thread = IPInfo(ip=item["IP"], name="")
                    thread.signals.infoSignal.connect(self.ActionsAfterIP)
                    self.poolIPInfo.start(thread)

    # Сохранение JSON в файл
    def closeEvent(self, event):
        with open("log.json", "w+", encoding="utf-8-sig") as f:
            json.dump(self.jsonPackets, f, ensure_ascii=False, sort_keys=True)
        with open("IPandNames.json", "w+", encoding="utf-8-sig") as f:
            json.dump(self.jsonIPandNames, f, ensure_ascii=False, sort_keys=True)

    # Открытие JSON из файла
    def openJSONPackets(self, Path):
        with open(Path, "a+", encoding="utf-8-sig") as data_file:
            data_file.seek(0)
            data = data_file.read()
            if data:
                j = json.loads(data)
                return j
            else:
                return []

        # Открытие JSON из файла

    def openJSONIPandNames(self, Path):
        with open(Path, "a+", encoding="utf-8-sig") as data_file:
            data_file.seek(0)
            data = data_file.read()
            if data:
                j = json.loads(data)
                for item in j:

                    if "IPInfo" not in item or (
                        "IPInfo" in item and "ISP" not in item["IPInfo"]
                    ):
                        thread = IPInfo(ip=item["IP"], name=item["ESO"])
                        thread.signals.infoSignal.connect(self.ActionsAfterIP)
                        self.poolIPInfo.start(thread)
                return j
            else:
                return []

    def MenuItem1Click(self):
        self.IPChecker.setVisible(False)
        self.Settings.setVisible(False)
        self.RecordedGame.setVisible(False)
        self.ESOPacketsLog.setVisible(True)

    def MenuItem2Click(self):
        self.ESOPacketsLog.setVisible(False)
        self.Settings.setVisible(False)
        self.RecordedGame.setVisible(False)
        self.IPChecker.setVisible(True)

    def MenuItem3Click(self):
        self.IPChecker.setVisible(False)
        self.ESOPacketsLog.setVisible(False)
        self.RecordedGame.setVisible(False)
        self.Settings.setVisible(True)

    def MenuItem4Click(self):
        self.IPChecker.setVisible(False)
        self.ESOPacketsLog.setVisible(False)
        self.Settings.setVisible(False)
        self.RecordedGame.setVisible(True)

    def GetMyDocumentsPath(self):

        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value

        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(
            None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf
        )

        return buf.value

    def OpenAndParse(self):
        self.ParseButton.setEnabled(False)
        FileName, _ = QFileDialog.getOpenFileName(
            self,
            self.loc["openlabel"],
            os.path.join(
                self.GetMyDocumentsPath(), "My Games", "Age of Empires 3", "Savegame"
            ),
            "Age of Empires 3 Records (*.age3rec *.age3Xrec *.age3Yrec)",
        )
        if FileName:
            thread = RecordGame(FileName)
            thread.signals.infoSignal.connect(self.DisplayRecordedGame)
            self.RecordedGamePool.start(thread)
        else:
            self.ParseButton.setEnabled(True)

    def getCivIconById(self, id):
        if id == 1:
            return QPixmap(self.getPath() + "Visuals/Civs/Spanish.png")
        elif id == 2:
            return QPixmap(self.getPath() + "Visuals/Civs/British.png")
        elif id == 3:
            return QPixmap(self.getPath() + "Visuals/Civs/French.png")
        elif id == 4:
            return QPixmap(self.getPath() + "Visuals/Civs/Portuguese.png")
        elif id == 5:
            return QPixmap(self.getPath() + "Visuals/Civs/Dutch.png")
        elif id == 6:
            return QPixmap(self.getPath() + "Visuals/Civs/Russians.png")
        elif id == 7:
            return QPixmap(self.getPath() + "Visuals/Civs/Germans.png")
        elif id == 8:
            return QPixmap(self.getPath() + "Visuals/Civs/Ottomans.png")
        elif id == 15:
            return QPixmap(self.getPath() + "Visuals/Civs/XPIroquois.png")
        elif id == 16:
            return QPixmap(self.getPath() + "Visuals/Civs/XPSioux.png")
        elif id == 17:
            return QPixmap(self.getPath() + "Visuals/Civs/XPAztec.png")
        elif id == 19:
            return QPixmap(self.getPath() + "Visuals/Civs/Japanese.png")
        elif id == 20:
            return QPixmap(self.getPath() + "Visuals/Civs/Chinese.png")
        elif id == 21:
            return QPixmap(self.getPath() + "Visuals/Civs/Indians.png")
        else:
            return QPixmap()

    def DisplayRecordedGame(self, data):
        if not data["Game"] or not data["Players"]:
            QMessageBox.warning(self, "ESO Tracker", self.loc["parsingwarning"])
        else:

            totalRealPlayers = data["Game"]["numplayers"]
            if data["Game"]["is_observer_ui"] == 1:
                if data["Players"]["1"]["teamid"] != data["Players"]["2"]["teamid"]:
                    totalRealPlayers = 2
                elif (
                    data["Game"]["numplayers"] > 2
                    and data["Players"]["2"]["teamid"] != data["Players"]["3"]["teamid"]
                ):
                    totalRealPlayers = 4
                elif (
                    data["Game"]["numplayers"] > 3
                    and data["Players"]["3"]["teamid"] != data["Players"]["4"]["teamid"]
                ):
                    totalRealPlayers = 6

            self.gameName.setText(data["Game"]["name"])
            if data["Game"]["exe_name"] == "age3t.exe":
                self.exeVersion.setText(
                    self.loc["Version"]
                    + "Treaty Patch "
                    + ".".join(list(data["Game"]["exe_version"].split(".")[-1]))
                )
            elif data["Game"]["exe_name"] == "age3f.exe":
                self.exeVersion.setText(
                    self.loc["Version"]
                    + "ESOC Patch "
                    + ".".join(list(data["Game"]["exe_version"].split(".")[-1]))
                )
            elif data["Game"]["exe_name"] == "age3y.exe":
                self.exeVersion.setText(self.loc["Version"] + "The Asian Dynasties")
            elif data["Game"]["exe_name"] == "age3.exe":
                self.exeVersion.setText(self.loc["Version"] + "Vanilla")
            elif data["Game"]["exe_name"] == "age3x.exe":
                self.exeVersion.setText(self.loc["Version"] + "The Warchiefs")
            else:
                self.exeVersion.setText(self.loc["Version"] + self.loc["unknown"])

            self.Map.setText(data["Game"]["filename"])

            if data["Game"]["modetype"] == 1:
                self.Mode.setText(
                    self.loc["Mode"]
                    + f"Deathmatch ({totalRealPlayers // 2}v{totalRealPlayers // 2})"
                )
            elif data["Game"]["modetype"] == 0:
                if data["Game"]["expansion"] != 0 and data["Game"]["norush"] > 0:
                    self.Mode.setText(
                        self.loc["Mode"]
                        + "Treaty "
                        + str(data["Game"]["norush"])
                        + self.loc["min."]
                        + f" ({totalRealPlayers // 2}v{totalRealPlayers // 2})"
                    )
                elif data["Game"]["expansion"] == 2 and data["Game"]["koth"] == b"\x01":
                    self.Mode.setText(
                        self.loc["Mode"]
                        + f"King of the Hill ({totalRealPlayers // 2}v{totalRealPlayers // 2})"
                    )
                else:
                    self.Mode.setText(
                        self.loc["Mode"]
                        + f"Supremacy ({totalRealPlayers // 2}v{totalRealPlayers // 2})"
                    )

            self.Duration.setText(
                self.loc["Duration"]
                + str(timedelta(milliseconds=data["Game"]["duration"]))
            )
            if self.Team1.layout() is not None:
                QWidget().setLayout(self.Team1.layout())
            if self.Team2.layout() is not None:
                QWidget().setLayout(self.Team2.layout())
            Team1Layout = QVBoxLayout(self.Team1)
            Team2Layout = QVBoxLayout(self.Team2)
            self.player1Name = QLabel()
            self.player1Name.setObjectName("GameInfo")
            self.player2Name = QLabel()
            self.player2Name.setObjectName("GameInfo")
            self.player3Name = QLabel()
            self.player3Name.setObjectName("GameInfo")
            self.player4Name = QLabel()
            self.player4Name.setObjectName("GameInfo")
            self.player5Name = QLabel()
            self.player5Name.setObjectName("GameInfo")
            self.player6Name = QLabel()
            self.player6Name.setObjectName("GameInfo")
            self.player7Name = QLabel()
            self.player7Name.setObjectName("GameInfo")
            self.player8Name = QLabel()
            self.player8Name.setObjectName("GameInfo")

            self.civ1 = QLabel()
            self.civ1.setFixedSize(38, 25)
            self.civ2 = QLabel()
            self.civ2.setFixedSize(38, 25)
            self.civ3 = QLabel()
            self.civ3.setFixedSize(38, 25)
            self.civ4 = QLabel()
            self.civ4.setFixedSize(38, 25)
            self.civ5 = QLabel()
            self.civ5.setFixedSize(38, 25)
            self.civ6 = QLabel()
            self.civ6.setFixedSize(38, 25)
            self.civ7 = QLabel()
            self.civ7.setFixedSize(38, 25)
            self.civ8 = QLabel()
            self.civ8.setFixedSize(38, 25)

            self.player1 = QWidget()
            self.player1.setMinimumHeight(25)
            player1Layout = QHBoxLayout(self.player1)
            player1Layout.addWidget(self.civ1)
            player1Layout.addWidget(self.player1Name, Qt.AlignVCenter)
            player1Layout.setContentsMargins(0, 0, 0, 0)

            self.player2 = QWidget()
            self.player2.setMinimumHeight(25)
            player2Layout = QHBoxLayout(self.player2)
            player2Layout.addWidget(self.civ2)
            player2Layout.addWidget(self.player2Name)
            player2Layout.setContentsMargins(0, 0, 0, 0)

            self.player3 = QWidget()
            self.player3.setMinimumHeight(25)
            player3Layout = QHBoxLayout(self.player3)
            player3Layout.addWidget(self.civ3)
            player3Layout.addWidget(self.player3Name)
            player3Layout.setContentsMargins(0, 0, 0, 0)

            self.player4 = QWidget()
            self.player4.setMinimumHeight(25)
            player4Layout = QHBoxLayout(self.player4)
            player4Layout.addWidget(self.civ4)
            player4Layout.addWidget(self.player4Name)
            player4Layout.setContentsMargins(0, 0, 0, 0)

            self.player5 = QWidget()
            self.player5.setMinimumHeight(25)
            player5Layout = QHBoxLayout(self.player5)
            player5Layout.addWidget(self.civ5)
            player5Layout.addWidget(self.player5Name)
            player5Layout.setContentsMargins(0, 0, 0, 0)

            self.player6 = QWidget()
            self.player6.setMinimumHeight(25)
            player6Layout = QHBoxLayout(self.player6)
            player6Layout.addWidget(self.civ6)
            player6Layout.addWidget(self.player6Name)
            player6Layout.setContentsMargins(0, 0, 0, 0)

            self.player7 = QWidget()
            self.player7.setMinimumHeight(25)
            player7Layout = QHBoxLayout(self.player7)
            player7Layout.addWidget(self.civ7)
            player7Layout.addWidget(self.player7Name)
            player7Layout.setContentsMargins(0, 0, 0, 0)

            self.player8 = QWidget()
            self.player8.setMinimumHeight(25)
            player8Layout = QHBoxLayout(self.player8)
            player8Layout.addWidget(self.civ8)
            player8Layout.addWidget(self.player8Name)
            player8Layout.setContentsMargins(0, 0, 0, 0)
            # player8Layout.addStretch(1)
            # FFALayout = QHBoxLayout()
            self.MapIcon.setFixedSize(180, 180)
            self.MapIcon.setPixmap(
                QPixmap(
                    os.path.join(
                        "Maps",
                        data["Game"]["filename"]
                        .lower()
                        .replace("tr snowy gp", "snowy_great_plains")
                        .replace(" ui(2,2c)", "")
                        .replace(" ui(2,2)", "")
                        .replace(" ui(2,2ca)", "")
                        .replace(" ui(2,2a)", "")
                        .replace(" ui(2,2b)", "")
                        .replace("uix esoc ", "")
                        .replace(" treaty 1,7r", "")
                        .replace("uix ", "")
                        .replace("ui 2,2 esoc ", "")
                        .replace("ui 2,2 ", "")
                        .replace("esoc ", "")
                        .replace(" ", "_")
                        + ".png",
                    )
                ).scaledToWidth(180, Qt.SmoothTransformation)
            )

            actions = []
            decks = []
            team1Score = 0
            team2Score = 0
            # print(data["Game"]["view_point"])
            for i in range(data["Game"]["numplayers"]):
                if str(i + 1) in data["Players"]:
                    pInfo = data["Players"][str(i + 1)]
                    pActions = pInfo["actions"]
                    pDecks = pInfo["decks"]
                    is_observer = pInfo["status"] != 0 or pInfo["id"] > totalRealPlayers
                    if is_observer:
                        continue
                    actions += list(
                        filter(
                            lambda x: x["type"] == "resigned"
                            or x["type"] == "train"
                            or x["type"] == "build"
                            or x["type"] == "shipment"
                            or x["type"] == "spawn_unit"
                            or x["type"] == "research_tech1"
                            or x["type"] == "research_tech2"
                            or x["type"] == "research_tech3"
                            or x["type"] == "pick_deck",
                            pActions,
                        )
                    )
                    if pInfo["selectedDeckId"] != -1:
                        for deck in pDecks:
                            if deck["id"] == pInfo["selectedDeckId"]:
                                decks.append(
                                    {"pName": pInfo["name"], "dName": deck["name"]}
                                )
                                currentAge = -1
                                for card in deck["cards"]:
                                    if isinstance(card, dict):
                                        if currentAge != int(card["age"]):
                                            currentAge = int(card["age"])
                                            decks.append(
                                                {"aName": "Age " + str(currentAge + 1)}
                                            )

                                        decks.append(card)
                                break
                    elif len(pDecks) > 0:
                        decks.append(
                            {"pName": pInfo["name"], "dName": pDecks[0]["name"]}
                        )
                        currentAge = -1
                        for card in pDecks[0]["cards"]:
                            if isinstance(card, dict):
                                if currentAge != int(card["age"]):
                                    currentAge = int(card["age"])
                                    decks.append(
                                        {"aName": "Age " + str(currentAge + 1)}
                                    )

                                decks.append(card)
                    if pInfo["teamid"] == 1:
                        team2Score += pInfo["is_resigned"]
                    else:
                        team1Score += pInfo["is_resigned"]

                    # print(len(pActions))
                    apm = int(len(pActions) // (data["Game"]["duration"] / 1000 / 60))

                    if pInfo["clan"]:
                        labelText = (
                            chr(0x200E)
                            + f"({pInfo['clan']}) {pInfo['name']} (PR {pInfo['powerrating']})\n"
                            + self.loc["apm"]
                            + f"{apm}"
                        )
                    else:
                        labelText = (
                            chr(0x200E)
                            + f"{pInfo['name']} (PR {pInfo['powerrating']})\n"
                            + self.loc["apm"]
                            + f"{apm}"
                        )
                    if i == 0:
                        self.player1Name.setText(labelText)
                        self.civ1.setPixmap(self.getCivIconById(pInfo["civ"]))
                        if pInfo["teamid"] == 1:
                            Team1Layout.addWidget(self.player1)
                        else:
                            Team2Layout.addWidget(self.player1)
                    if i == 1:
                        self.player2Name.setText(labelText)
                        self.civ2.setPixmap(self.getCivIconById(pInfo["civ"]))
                        if pInfo["teamid"] == 1:
                            Team1Layout.addWidget(self.player2)
                        else:
                            Team2Layout.addWidget(self.player2)

                    if i == 2:
                        self.player3Name.setText(labelText)
                        self.civ3.setPixmap(self.getCivIconById(pInfo["civ"]))
                        if pInfo["teamid"] == 1:
                            Team1Layout.addWidget(self.player3)
                        else:
                            Team2Layout.addWidget(self.player3)
                    if i == 3:
                        self.player4Name.setText(labelText)
                        self.civ4.setPixmap(self.getCivIconById(pInfo["civ"]))
                        if pInfo["teamid"] == 1:
                            Team1Layout.addWidget(self.player4)
                        else:
                            Team2Layout.addWidget(self.player4)
                    if i == 4:
                        self.player5Name.setText(labelText)
                        self.civ5.setPixmap(self.getCivIconById(pInfo["civ"]))
                        if pInfo["teamid"] == 1:
                            Team1Layout.addWidget(self.player5)
                        else:
                            Team2Layout.addWidget(self.player5)
                    if i == 5:
                        self.player6Name.setText(labelText)
                        self.civ6.setPixmap(self.getCivIconById(pInfo["civ"]))
                        if pInfo["teamid"] == 1:
                            Team1Layout.addWidget(self.player6)
                        else:
                            Team2Layout.addWidget(self.player6)
                    if i == 6:
                        self.player7Name.setText(labelText)
                        self.civ7.setPixmap(self.getCivIconById(pInfo["civ"]))
                        if pInfo["teamid"] == 1:
                            Team1Layout.addWidget(self.player7)
                        else:
                            Team2Layout.addWidget(self.player7)
                    if i == 7:
                        self.player8Name.setText(labelText)
                        self.civ8.setPixmap(self.getCivIconById(pInfo["civ"]))
                        if pInfo["teamid"] == 1:
                            Team1Layout.addWidget(self.player8)
                        else:
                            Team2Layout.addWidget(self.player8)
            if team1Score > team2Score:
                self.Team1.setObjectName("TeamWon")
                self.Team2.setObjectName("TeamLost")
            elif team2Score > team1Score:
                self.Team2.setObjectName("TeamWon")
                self.Team1.setObjectName("TeamLost")
            else:
                self.Team2.setObjectName("TeamNone")
                self.Team1.setObjectName("TeamNone")


            FilterPattern = {"colors": [], "actions": []}
            if self.player1Color.isChecked():
                FilterPattern["colors"].append(playerColors[0])
            if self.player2Color.isChecked():
                FilterPattern["colors"].append(playerColors[1])
            if self.player3Color.isChecked():
                FilterPattern["colors"].append(playerColors[2])
            if self.player4Color.isChecked():
                FilterPattern["colors"].append(playerColors[3])
            if self.player5Color.isChecked():
                FilterPattern["colors"].append(playerColors[4])
            if self.player6Color.isChecked():
                FilterPattern["colors"].append(playerColors[5])
            if self.player7Color.isChecked():
                FilterPattern["colors"].append(playerColors[6])
            if self.player8Color.isChecked():
                FilterPattern["colors"].append(playerColors[7])

            if self.cbBuild.isChecked():
                FilterPattern["actions"].append("build")
            if self.cbPickDeck.isChecked():
                FilterPattern["actions"].append("pick_deck")
            if self.cbResearchCheatTech.isChecked():
                FilterPattern["actions"].append("research_tech2")
                FilterPattern["actions"].append("research_tech3")
            if self.cbResearchTech.isChecked():
                FilterPattern["actions"].append("research_tech1")
            if self.cbResigned.isChecked():
                FilterPattern["actions"].append("resigned")
            if self.cbShipment.isChecked():
                FilterPattern["actions"].append("shipment")
            if self.cbSpawnUnit.isChecked():
                FilterPattern["actions"].append("spawn_unit")
            if self.cbTrain.isChecked():
                FilterPattern["actions"].append("train")


            self.DeckModel = DeckListModel(decks)
            self.Decks.setModel(self.DeckModel)
            self.Decks.setWordWrap(True)
            self.PlayerActionsModel = PlayerActionsListModel(actions, data["Players"])
            self.PlayerActions.setWordWrap(True)
            self.PlayerActionsFilterModel = PlayerActionsProxyModel(
                FilterPattern, self.PlayerActionsModel
            )
            self.PlayerActionsFilterModel.sort(0, Qt.AscendingOrder)
            self.PlayerActions.setModel(self.PlayerActionsFilterModel)

            self.Team1.style().unpolish(self.Team1)
            self.Team1.style().polish(self.Team1)
            self.Team2.style().unpolish(self.Team2)
            self.Team2.style().polish(self.Team2)

            # print(data["Game"])
        self.ParseButton.setEnabled(True)


if __name__ == "__main__":
    sys.stdout = open("stdout.txt", "a+")
    app = QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())
