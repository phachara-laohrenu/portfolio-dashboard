import requests
import re
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import date
import time

import ftscraper as ft
from finnomena_api import finnomenaAPI

class fundObj(object):
    """Class which contains each search result when searching data in Financial Times.
    
    This class contains the search results of the ft.com search made with the function
    call `ftscraper.search(search)` which returns a :obj:`list` 
    of instances of this class with the formatted retrieved information.
    """

    def __init__(self, sec_name):
        """
        sec_name: Thai Fund name
        """
        self.finnoapi = finnomenaAPI()

        self.sec_name = sec_name
        self.fund_info = self.finnoapi.get_fund_info(self.sec_name)
        print(self.fund_info['feeder_fund'])
        self.feeder_obj = None
        self.feeder_info = self.get_feeder_info()
        
        # for k, v in dictionary.items():
        #     setattr(self, k, v)

    def get_feeder_info(self):
        """
        Get information of the feeder fund (if any)
        """
        if self.fund_info['feeder_fund'] is None:
            return None
        self.feeder_obj = ft.search_select_fund(self.fund_info['feeder_fund'])
        feeder_info = self.feeder_obj.get_summary()
        return feeder_info
    
    def get_historical(self):
        """
        Get historical prices of the fund
        """
        return self.finnoapi.get_fund_price(self.sec_name)

    def get_feeder_historical(self):
        """
        Get historical prices of the feeder fund (if any)
        """
        return self.feeder_obj.get_historical()
        
