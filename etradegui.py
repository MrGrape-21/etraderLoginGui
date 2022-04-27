from __future__ import print_function
import webbrowser
import json
import logging
import configparser
import sys
import requests
from rauth import OAuth1Service
from logging.handlers import RotatingFileHandler

from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import *
from settingwidgets import *

from etradeagent import *
from etradeaccount import Accounts, Market
from etradeorder import Order

# logger settings
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler("etradeAPI.log", maxBytes=5*1024*1024, backupCount=3)
FORMAT = "%(asctime)-15s %(message)s"
fmt = logging.Formatter(FORMAT, datefmt='%m/%d/%Y %I:%M:%S %p')
handler.setFormatter(fmt)
logger.addHandler(handler)


class etradeGUI(QWidget):

    def __init__(self, agt, parent=None):
        super().__init__(parent)

        self.agent = agt
        self.market = None
        self.orders = None
        self.accounts = None

        self.setupUI()
        self.connections()

    def setupUI(self):
        uic.loadUi('etradegui.ui', self)
        self.setWindowOpacity(1.0)
        self.setAutoFillBackground(True)

        self.GUI_dict = {
            "setup": self.pushButton_setup,
            "plotting": self.pushButton_plot,
            "closeGUI": self.pushButton_close,
            "balance": self.pushButton_balance,
            "auto": self.pushButton_auto,
            "tradable": self.pushButton_tradable,
            "orders": self.pushButton_orders,
            "fund": self.label_fund,
            "summary": self.label_summary,
            "orderReview": self.tableWidget_review,
            "trademonitor": self.tableWidget_monitor,
            "tradeSummary": self.tableWidget_summary,
            "gvPlotting": self.graphicsView_plot
        }

        setPushButton(self.GUI_dict["setup"], self.agent.stat)
        self.GUI_dict["closeGUI"].clicked.connect(self.close)
        self.GUI_dict["closeGUI"].setStyleSheet("background-color: rgb(255, 0, 0);")
        self.isAgentReady(self.agent.stat)
        if self.orders is None:
            self.GUI_dict["orders"].setEnabled(False)

        self.GUI_dict["balance"].clicked.connect(self.balanceRvw)
        self.GUI_dict["tradable"].clicked.connect(self.marketRvw)
        self.GUI_dict["orders"].clicked.connect(self.orderRvw)
        self.GUI_dict["plotting"].clicked.connect(self.plots)


    def isAgentReady(self, stat):
        self.GUI_dict["balance"].setEnabled(stat)
        self.GUI_dict["tradable"].setEnabled(stat)
        self.GUI_dict["plotting"].setEnabled(stat)
        self.GUI_dict["auto"].setEnabled(stat)
        #self.GUI_dict["orders"].setEnabled(stat)

    def connections(self):
        self.GUI_dict["setup"].clicked.connect(self.oauthAPI)

    def oauthAPI(self):
        self.ex = oauthWidget(self.agent, self)
        self.ex.sessionReady.connect(self.sessionReady)

    def getAgent(self):
        print("get back agent")
        return self.agent

    def sessionReady(self):
        self.agent = self.ex.getAgent()
        setPushButton(self.GUI_dict["setup"], self.agent.stat)
        self.isAgentReady(self.agent.stat)

    def balanceRvw(self):
        self.accounts = Accounts(self.agent.session, self.agent.authService.base_url)
        self.accounts.account_list()

    def marketRvw(self):
        self.market = Market(self.agent.session, self.agent.authService.base_url)

        self.market.quotes()

    def orderRvw(self):
        self.order = Order(self.agent.session, self.accounts, self.agent.authService.base_url)

    def plots(self):
        print("plot recent gain/loss")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    agt = brokerAgent()

    window = etradeGUI(agt)

    window.show()

    sys.exit(app.exec_())
