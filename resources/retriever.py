import yaml
import requests
import pandas as pd
from datetime import datetime
from dateutil import relativedelta
import os
from tqdm import tqdm
from finnomena_api import finnomenaAPI as finnoapi
import ftscraper as ft

from resources.utils import *
from resources.fund_obj import fundObj

# assets = load_yaml('assets.yaml')
# keys = load_yaml('keys.yaml')


class Retriever:
    def __init__(self):
        pass

    def get_fund_obj(self, query, source='finnomena'):
        """
        Get a fund by given query from finnomena
        """
        fund_obj = fundObj(query)
        return fund_obj

    def construct_timeseries(self, data, start_date=None, end_date=None):
        """
        arg
            data: [{'date':[d0,d1,d2,d3,...,dn], <col1>:[c0,c1,c2,c3,...,cn], <col2>: ......},
                   {'date':[d0,d1,d2,d3,...,dn], <col1>:[c0,c1,c2,c3,...,cn], <col2>: ......},
                   ....
                   ]
        """
        if isinstance(data, pd.DataFrame):
            data = data.to_dict(orient='list')

        if start_date is None:
            start_dates = []
            for d in data:
                start_dates.append(datetime.strptime(d['date'][0], '%Y-%m-%d'))
            start_date = min(start_dates)
            start_date = start_date.strftime('%Y-%m-%d')
        
        dates_list = get_dates(start_date, end_date)
        df = pd.DataFrame(index=dates_list)
        for d in data:
            dft = pd.DataFrame(d)
            dft.set_index('date', inplace=True)
            dft = remove_weekends(dft)
            df = pd.concat([df,dft], axis=1)
        return df

    def combine_timeseries(self, fund_list):
        
        data = []

        for fund_name in fund_list:
            fund_obj = self.get_fund_obj(fund_name)
            print(fund_name)
            
            if fund_obj.feeder_obj is None:
                dft = fund_obj.get_historical()
                dft = dft.rename(columns={'price':fund_name})
            else:
                dft = fund_obj.get_feeder_historical()
                dft = dft.filter(items=['date','close'])
                dft = dft.rename(columns={'close':fund_name + ' [feeder]'})
            
            dft_dict = dft.to_dict(orient='list')
            data.append(dft_dict)
        
        df = self.construct_timeseries(data)

        return df

            
            