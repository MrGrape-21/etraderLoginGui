#   etrade agent,
#   interactive with etradegui to configure service, start oauth1.0 session

import os

import webbrowser
import json
import logging
import configparser
import requests
from rauth import OAuth1Service


#   should avoid to directly login this for security, but it will be used if under the working Dir
defaultConfig = 'config.ini'


def configReadin(configPath):
    config = configparser.ConfigParser()
    config.read(configPath)
    return config


def validateConfigIni(configPath):
    if os.path.isfile(configPath) and os.stat(configPath).st_size > 0:
        cfg = configReadin(configPath)
        return True, cfg
    else:
        return False, None


class brokerAgent(object):
    """
    agent oauth1 service
    """
    def __init__(self):
        self.stat = False
        self.config = None
        self.session = None

        self.authService = OAuth1Service(
            name="etrade",
            consumer_key="123",
            consumer_secret="456",
            request_token_url="https://api.etrade.com/oauth/request_token",
            access_token_url="https://api.etrade.com/oauth/access_token",
            authorize_url="https://us.etrade.com/e/t/etws/authorize?key={}&token={}",
            base_url="https://api.etrade.com")

        self.market = None
        self.accounts = None
        self.orders = None

    def cfgAgent(self, cfg):
        self.authService.consumer_key = cfg["DEFAULT"]["CONSUMER_KEY"]
        self.authService.consumer_secret = cfg["DEFAULT"]["CONSUMER_SECRET"]

    #   load config.ini from a file, fname
    def cfgAgentFromFile(self, fname):
        self.stat, self.config = validateConfigIni(fname)
        if self.stat:
            self.cfgAgent(self.config)






