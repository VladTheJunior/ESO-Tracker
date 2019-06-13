from scapy.all import traceroute
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal

class LobbySignals(QObject):
    playerinLobby = pyqtSignal(dict)

class pingIP(QRunnable):
    def __init__(self, ip):
        super().__init__()
        self.ip = ip
        self.signals = LobbySignals()

    def run(self):
        result, _ = traceroute(self.ip, verbose=False)

        # r = [(snd, recv) for snd, recv in result if snd.dst == self.ip]
        maxttl = max(result, key=lambda x: x[0].ttl)[0].ttl
        stat = [(snd, recv) for snd, recv in result if snd.ttl == maxttl]
        self.signals.playerinLobby.emit(
            {
                "IP": stat[0][0].dst,
                "RTT": f"{round(1000*(stat[0][1].time - stat[0][0].sent_time))} ms",
            }
        )