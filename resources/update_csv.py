import pandas as pd
from google.cloud import storage
from io import StringIO
from finnomena_api import finnomenaAPI
import os
from datetime import datetime
import yaml

from resources.utils import load_yaml, download_blob


class UpdateCSV():
    def __init__(self, usr_pass, bucket_name='portfolio-dashboard-poch.appspot.com'):
        self.storage_client = storage.Client()
        self.bucket_name = bucket_name

        self.file_name_dict = load_yaml('config/keys.yaml')['file_name']

        self.blobs = self.get_blobs()

        self.usr_pass = usr_pass

        self.finno_api = finnomenaAPI(email=self.usr_pass['finnomena']['usr'], password=self.usr_pass['finnomena']['password'])


    def upload_blob(self, data, destination_blob_name):
        """Uploads a file to the bucket."""
        bucket = self.storage_client.bucket(self.bucket_name)
        blob = bucket.blob(destination_blob_name)
        if isinstance(data, pd.DataFrame):
            blob.upload_from_string(data.to_csv(), 'text/csv')
        elif isinstance(data, dict):
            blob.upload_from_string(yaml.dump(data),'application/octet-stream')

    
    def download_blob(self, blob_name,header=0):
        data = download_blob(self.storage_client, self.bucket_name, blob_name, header=header)      
        return data
    
    def get_blobs(self):
        blobs = self.storage_client.list_blobs(self.bucket_name)
        blobs = [blob.name for blob in blobs]
        return blobs
    
    def update_file(self, append, file_name, drop_dup = True, subset=None, header=0):

        if file_name not in self.blobs:
            self.upload_blob(append, file_name)
        else:
            df0 = self.download_blob(file_name, header)

            if drop_dup:
                file = pd.concat([df0, append]).drop_duplicates()
            else:
                file = pd.concat([df0, append])
    
            self.upload_blob(file, file_name)


    def update_finno_port(self):
        _, historical_value, _ = self.finno_api.get_port_status("DIY")
        historical_value = historical_value.set_index('portfolio_date')

        self.update_file(historical_value, self.file_name_dict['finno_port_status'])

    def update_finno_sec_com(self):
        _, _, compositions = self.finno_api.get_port_status("DIY")
        portfolio_date = compositions['portfolio_date'][0]
        compositions = compositions[['sec_name','nav_date', 'market_value', 'weight', 'return', 'cost', 'total_unit', 'avg_price', 'current_nav']]
        compositions = compositions.set_index('sec_name')
        columns = []
        for i in compositions.index:
            for j in compositions.columns:
                columns.append((i,j))

        compositions = pd.DataFrame([compositions.values.flatten()], columns=columns)
        compositions.columns = pd.MultiIndex.from_tuples(compositions.columns, names=['sec_name','attributes'])
        compositions.index = [portfolio_date]

        self.update_file(compositions, self.file_name_dict['finno_port_compo'], header=[0,1])
    
    def update_log(self):
        now = datetime.now()
        dt_string = now.strftime("%Y/%m/%d %H:%M:%S") + ' (UTC)'
        df = pd.DataFrame([dt_string], columns=['update_time'])

        self.update_file(df, self.file_name_dict['update_log'])

    def update_feeder(self, secs):
        # check 
        file_name = self.file_name_dict['feeder_info']
        if file_name in self.blobs:
            feeder_dict = self.download_blob(file_name)
        else:
            feeder_dict = {}

        intersection = list(set(feeder_dict.keys()) & set(secs))

        for fund_name in secs:
            if fund_name in intersection:
                continue

            fund_obj = self.get_fund_obj(fund_name)
            
            if fund_obj.feeder_obj is None:
                feeder_dict[fund_name] = None
            else:
                feeder_name = fund_obj.fund_info['feeder_fund']
                feeder_fullname = fund_obj.feeder_obj.sec_name
                feeder_info = {'fullname':fund_obj.feeder_obj.sec_name,
                               'symbol':fund_obj.feeder_obj.symbol,
                               'xid':fund_obj.feeder_obj.get_idx()
                               'allocation':1}
                feeder_dict[fund_name] = {feeder_name: feeder_info}
        
        # upload
        self.upload_blob(feeder_dict, file_name)
        

                
        