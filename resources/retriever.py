import yaml
import requests
import pandas as pd
from datetime import datetime
from dateutil import relativedelta
import os
from tqdm import tqdm

from resources.utils import *

# assets = load_yaml('assets.yaml')
# keys = load_yaml('keys.yaml')


class Retriever:

    def __init__(self, config_path = 'config'):
        self.config = {}
        for f in os.listdir(config_path):
            self.config[os.path.splitext(f)[0]] = load_yaml(config_path + '/' + f)

        self.sources_list = list(self.config['keys']['sources'].keys())
        #self.isin_dict, _ = get_asset_from_info('ISIN')
        self.asset_info = get_assetinfotable()
        #self.assetType_dict, _ = get_assetType()

    def get(self, source: str, time_range: str, ISIN: str = None, asset_name: str = None):
        # Check if source is valid 
        assert source in self.sources_list

        # Check ISIN and asset_name
        if ISIN is not None and asset_name is not None:
            isin_tmp = self.config['assets']['asset_library']['asset_type'][asset_name]['ISIN']
            assert isin_tmp == ISIN
        elif ISIN is None and asset_name is not None:
            #ISIN = self.config['assets']['asset_library']['asset_type'][asset_name]['ISIN']
            asset = self.asset_info.loc[asset_name]
        elif ISIN is not None and asset_name is None:
            asset = self.asset_info[self.asset_info['ISIN'] == ISIN].index[0]
        else:
            raise Exception("only either ISIN or asset_name can be None")

        # Infer type of asset
        asset_type = asset['asset_type']
        
        asset_id = asset[source + '_id']
        url = self.config['keys']['sources'][source]['url']['timeseries_price']

        if source == 'financialtimes': 
            df = self.get_financialtimes(url, asset_id, time_range)

        elif source == 'morningstar':
            df = self.get_morningstar(url, asset_id, time_range)
        
        elif source == 'finnomena':
            pass

        else:
            raise Exception("Invalid source: " + source)

        return df

    def get_current(self, time_range: str, source: str = 'financialtimes', master_fund = True):
        """
        Get dataframe of current assets in the portfolio

        arg:
            master_fund: bool. If True, use master funds data if available.
        """
        
        data = []
        for asset_name in self.config['port']['current_assets']:
            master_fund = self.asset_info.loc[asset_name]['master_fund']
            if (master_fund is not None) and (master_fund):
                source = 'financialtimes'
                print('retrieving: ' + master_fund + '\nfrom: ' + source + '\nfor: ' + asset_name)
                target_asset_name = master_fund
                
            else:
                source = 'finnomena'
                print('retrieving: ' + master_fund + '\nfrom: ' + source)
                target_asset_name = asset_name
            print('---------------------------------------------------------------------------------')
                
            df = self.get(source=source, time_range=time_range, asset_name=target_asset_name)
            data.append(df)
        
        final_df = pd.concat((iDF for iDF in data),axis=1, join='outer')
        final_df = final_df.sort_index()

        return final_df

    def get_morningstar(self, url: str, asset_id: str, time_range: str):
        asset = self.asset_info[self.asset_info['morningstar_id'] == asset_id]
        asset_name = asset.index[0]

        payload = {'currencyId': 'USD',
                    'idtype': 'Morningstar',
                    'frequency': 'daily',
                    'startDate':  get_start_date(time_range),
                    'performanceType': '',
                    'outputType': 'COMPACTJSON',
                    'id': asset_id,
                    'decPlaces': '8',
                    'applyTrackRecordExtension': 'false'}
        
        temp_data = requests.get(url, params=payload).json()
        df = pd.DataFrame(temp_data)
        df['timestamp'] = pd.to_datetime(df[0], unit='ms')
        df['date'] = df['timestamp'].dt.date 
        df = df[['date',1]]  
        df.columns = ['date', asset_name]
        df.set_index('date', inplace=True)

        return df

    def get_financialtimes(self, url: str, asset_id: str, time_range: str):

        asset = self.asset_info[self.asset_info['financialtimes_id'] == asset_id]
        asset_name = asset.index[0]

        payload = {'startDate':  get_start_date(time_range, splitter = '/'),
           'endDate': datetime.now().strftime('%Y/%m/%d'),
           'symbol': asset_id}

        temp_data = requests.get(url, params=payload).json()

        temp_data = temp_data['html']

        splitter1 = '<tr><td class="mod-ui-table__cell--text"><span class="mod-ui-hide-small-below">'
        splitter2 = '</span><span class="mod-ui-hide-medium-above">'
        splitter3 = '</span></td><td>'
        splitter4 = '</td><td>'
        data = {'date':[], asset_name:[]}
        for a in reversed(temp_data.split(splitter1)[1:]):
            split1 = a.split(splitter2)[1].split(splitter3)
            date = split1[0]
            m, d, y = date.split(' ')[1:]
            d = d[:-1]
            m = '%02d' % monthname2num(m)
            date = '-'.join([y,m,d])

            price = split1[1].split(splitter4)[0].replace(',', '')
            data['date'].append(date)
            data[asset_name].append(float(price))

        df = self.construct_timeseries([data])

        return df

    def get_finnomena(self, url: str, asset_id: str, time_range: str):
        # Validate time_range (available options are 1D, 7D, 1M, 3M, 6M, 1Y, 3Y, 5Y, 10Y and MAX)
        time_range_option = ['1D', '7D', '1M', '3M', '6M', '1Y', '3Y', '5Y', '10Y', 'MAX']
        assert time_range in time_range_option

        asset = self.asset_info[self.asset_info['finnomena_id'] == asset_id]
        asset_name = asset.index[0]

        payload = {'range':  time_range,
                   'fund': asset_id}

        temp_data = requests.get(url, params=payload).json()

        data = {'date':[], asset_name:[]}
        for i in temp_data:
            data['date'].append(i['nav_date'])
            data[asset_name].append(i['value'])
        
        df = self.construct_timeseries([data])

        return df


    def construct_timeseries(self, data, start_date=None, end_date=None):
        """
        arg
            data: [{'date':[d0,d1,d2,d3,...,dn], <col1>:[c0,c1,c2,c3,...,cn], <col2>: ......},
                   {'date':[d0,d1,d2,d3,...,dn], <col1>:[c0,c1,c2,c3,...,cn], <col2>: ......},
                   ....
                   ]
        """
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
            df = pd.concat([df,dft], axis=1)
        return df
