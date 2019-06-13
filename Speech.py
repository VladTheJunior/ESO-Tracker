import locale
import os.path
import random
import string
import sys
import winreg
from googletrans import Translator
from gtts import gTTS
from PyQt5.QtCore import QRunnable, pyqtSignal

import localization
from playsound import playsound


class Speech(QRunnable):
    def __init__(self, speechType, text, who, soundsFilter):
        super().__init__()
        self.speechType = speechType
        self.text = text
        self.who = who
        self.soundsFilter = soundsFilter
        self.lang = list(locale.getdefaultlocale())[0][0:2]

        if self.lang == "ru":
            self.loc = localization.ru
        else:
            self.loc = localization.en

    def playTaunt(self, name):
        gamePath = self.getGamePath()
        if gamePath is not None:
            try:
                playsound(os.path.join(gamePath, "Sound", "Taunts", name), block=False)
            except:
                pass

    def getGamePath(self):
        try:
            registry_key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\microsoft games\age of empires 3 expansion pack 2\1.0",
                0,
                winreg.KEY_READ,
            )
            value, _ = winreg.QueryValueEx(registry_key, "setuppath")
            winreg.CloseKey(registry_key)
            return value
        except WindowsError:
            return None                            

    def getSoundsPath(self):
        if getattr(sys, "frozen", False):
            # we are running in a bundle
            return os.path.join(sys._MEIPASS, "sound")
        else:
            # we are running in a normal Python environment
            return os.path.dirname(os.path.abspath(__file__))

    def run(self):
        try:
            soundPath = self.getSoundsPath()
            if self.speechType == "taunts":
                if self.soundsFilter["Messages"]:
                    self.playTaunt(self.text)
            elif self.speechType == "friends":
                if self.soundsFilter["Notifications"]:
                    playsound(os.path.join(soundPath, "connect.mp3"))
                if self.soundsFilter["Friends"]:
                    tts = gTTS(self.text, lang=self.loc["language"])
                    sound = "".join(
                        random.choices(string.ascii_uppercase + string.digits, k=32)
                    )
                    tts.save(os.path.join("TTS", sound + ".mp3"))
                    playsound(os.path.join("TTS", sound + ".mp3"))
            elif self.speechType == "connection":
                if self.soundsFilter["Notifications"]:
                    playsound(os.path.join(soundPath, "connect.mp3"))
                if self.soundsFilter["Connection"]:
                    tts = gTTS(self.text, lang=self.loc["language"])
                    sound = "".join(
                        random.choices(string.ascii_uppercase + string.digits, k=32)
                    )
                    tts.save(os.path.join("TTS", sound + ".mp3"))
                    playsound(os.path.join("TTS", sound + ".mp3"))
            elif self.speechType == "translateFromUDP":
                if self.soundsFilter["Notifications"]:
                    playsound(os.path.join(soundPath, "message.mp3"))
                if self.soundsFilter["Messages"]:
                    # if text language is not native -> translate it
                    translator = Translator()
                    detected_lang = translator.detect(self.text).lang
                    if detected_lang != self.lang:
                        self.text = translator.translate(self.text, dest=self.lang).text
                    tts = gTTS(self.text, lang=self.lang)
                    sound = "".join(
                        random.choices(string.ascii_uppercase + string.digits, k=32)
                    )
                    tts.save(os.path.join("TTS", sound + ".mp3"))
                    playsound(os.path.join("TTS", sound + ".mp3"))

            elif self.speechType == "translateFromTCP":
                if self.soundsFilter["Notifications"]:
                    playsound(os.path.join(soundPath, "message.mp3"))
                if self.soundsFilter["Messages"]:
                    # if text language is not native -> translate it
                    translator = Translator()
                    detected_lang = translator.detect(self.text).lang
                    if detected_lang != self.lang:
                        self.text = translator.translate(self.text, dest=self.lang).text
                    tts = gTTS(self.text, lang=self.lang)
                    sound = "".join(
                        random.choices(string.ascii_uppercase + string.digits, k=32)
                    )
                    tts.save(os.path.join("TTS", sound + ".mp3"))

                    tts2 = gTTS(self.who, lang=self.loc["language"])
                    sound2 = "".join(
                        random.choices(string.ascii_uppercase + string.digits, k=32)
                    )
                    tts2.save(os.path.join("TTS", sound2 + ".mp3"))

                    playsound(os.path.join("TTS", sound2 + ".mp3"))
                    playsound(os.path.join("TTS", sound + ".mp3"))

        except Exception as e:
            pass
