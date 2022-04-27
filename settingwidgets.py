#   config etrade agent from Config.ini (associated with Etrade private accounts, keep stored in a secure location)
#   execute etrade authorization and start a valid session

from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import os
import sys
sys.path.append('../customWidgets')
from stringSpinBox import stringSpinBox

from etradeagent import *


def setPushButton(gui_wgt, ctl):
    if ctl:
        gui_wgt.setStyleSheet("color: rgb(0, 0, 0); background-color: rgb(0, 255, 0)")
    else:
        gui_wgt.setStyleSheet("color: rgb(0, 0, 0); background-color: rgb(255, 0, 0)")


#   widget to config the etrade service authorization
#   emit a signal once a session established, use getAgent() to get the etrade agent with the session and base_url
class oauthWidget (QWidget):
    """
        GUI to configure the etrade service and establish an oauth 1.0 session
    """
    sessionReady = pyqtSignal()

    def __init__(self, agt, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        uic.loadUi('oauthwgt.ui', self)

        self.agent = agt
        setPushButton(self.pushButton_cfg, self.agent.stat)
        self.isAgtReady(self.agent.stat)

        self.pushButton_cfg.clicked.connect(self.findCFG)

        self.spinBox_ckey.setStrings(["SANDBOX_BASE_URL", "PROD_BASE_URL"], "SANDBOX_BASE_URL")
        self.spinBox_ckey.setToolTip("Select Consumer Key Type")
        self.spinBox_ckey.textChanged.connect(self.setCKey)

        self.pushButton_start.clicked.connect(self.startSession)

        self.lineEdit_code.returnPressed.connect(self.textCode)

        self.label_stat.setText("Session off")
        self.label_stat.setStyleSheet("background-color: rgb(255, 0, 0);color:rgb(255, 255, 0)")

        self.pushButton_close.clicked.connect(self.close)

        self.show()

    def findCFG(self):
        if self.agent.stat:
            self.agent.authService.base_url = self.agent.config["DEFAULT"][self.spinBox_ckey.text()]
            print("well set, ready to go", self.agent.authService.base_url)
            return

        fname, dummy = QFileDialog.getOpenFileName(self, 'Open file', 'c:\\', "Config files (*.ini)")
        if fname == "":
            return

        self.readConfigIni(fname)

        if self.agent.stat:
            self.agent.authService.base_url = self.agent.config["DEFAULT"][self.spinBox_ckey.text()]
            print("base url set to go", self.agent.authService.base_url)

    def isAgtReady(self, stat):
        if stat:
            self.spinBox_ckey.setVisible(True)
            self.pushButton_start.setVisible(True)
            self.label.setVisible(True)
            self.lineEdit_code.setVisible(True)
        else:
            self.spinBox_ckey.setHidden(True)
            self.pushButton_start.setHidden(True)
            self.label.setHidden(True)
            self.lineEdit_code.setHidden(True)

    def readConfigIni(self, fname):
        self.agent.cfgAgentFromFile(fname)
        setPushButton(self.pushButton_cfg, self.agent.stat)
        self.isAgtReady(self.agent.stat)

    #   the signal receiver calls this function to get the functioned etrade agent
    def getAgent(self):
        return self.agent

    def setCKey(self, ckey):
        self.agent.authService.base_url = self.agent.config["DEFAULT"][self.spinBox_ckey.text()]

    #   request authorization, etrade user login required in the popup browser
    def startSession(self):
        self.request_token, self.request_token_secret = self.agent.authService.get_request_token(
            params={"oauth_callback": "oob", "format": "json"})

        authorize_url = self.agent.authService.authorize_url.format(self.agent.authService.consumer_key,
                                                                    self.request_token)
        webbrowser.open(authorize_url)

    #   enter the text code from the popup browser to start an authenticated OAuth 1 session
    #   emit the session ready signal, turn the status label green
    def textCode(self):
        text_code = self.lineEdit_code.text()

        self.agent.authService.base_url = self.agent.config["DEFAULT"][self.spinBox_ckey.text()]
        self.agent.session = self.agent.authService.get_auth_session(self.request_token,
                                                                     self.request_token_secret,
                                                                     params={"oauth_verifier": text_code})

        self.sessionReady.emit()
        self.label_stat.setText("Session on")
        self.label_stat.setStyleSheet("background-color: rgb(0, 255, 0);color:rgb(255, 255, 255)")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(QColor(0, 0, 0, 255), 2)
        painter.setPen(pen)
        brush = QBrush(QColor(0, 100, 200, 250))
        painter.setBrush(brush)

        path = QPainterPath()
        rect = event.rect()
        rect.adjust(2, 2, -2, -2)
        path.addRoundedRect(QRectF(rect), 25, 25)

        painter.fillPath(path, painter.brush())
        painter.strokePath(path, painter.pen())

        super().paintEvent(event)

if __name__ == "__main__":
    import sys

    App = QApplication(sys.argv)

    window = oauthWidget()
    window.show()
    # start the app
    sys.exit(App.exec())
