import pandas as pd
from google.cloud import storage
from io import StringIO
from finnomena_api import finnomenaAPI
import os
from datetime import datetime

from resources.utils import load_yaml, download_blob_csv


class UpdateCSV():
    def __init__(self, usr_pass, credential_folder = 'gcs_cred', bucket_name='portfolio-dashboard-poch.appspot.com'):
        self.credential_path = credential_folder + '/' + os.listdir(credential_folder)[0]
        self.storage_client = storage.Client.from_service_account_json(self.credential_path)
        self.bucket_name = bucket_name

        self.finno_port_csv = 'finno_port_status.csv'
        self.finno_compo_csv = 'finno_port_compo.csv'
        self.blobs = self.get_blobs()

        self.usr_pass = usr_pass


    def upload_blob(self, df, destination_blob_name):
        """Uploads a file to the bucket."""
        bucket = self.storage_client.bucket(self.bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(df.to_csv(), 'text/csv')
    
    def download_blob(self, blob_name,header=0):

        df = download_blob_csv(self.storage_client, self.bucket_name, blob_name, header=header)      
        # bucket = self.storage_client.get_bucket(self.bucket_name)
        # blob = bucket.blob(blob_name)
        # downloaded_blob = blob.download_as_bytes()
        # s = str(downloaded_blob,'utf-8')
        # data = StringIO(s) 
        # df = pd.read_csv(data)
        return df
    
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
        finno_api = finnomenaAPI(email=self.usr_pass['finnomena']['usr'], password=self.usr_pass['finnomena']['password'])
        _, historical_value, _ = finno_api.get_port_status("DIY")
        historical_value = historical_value.set_index('portfolio_date')

        self.update_file(historical_value, self.finno_port_csv)

        # file_name = self.finno_port_csv
        # if file_name not in self.blobs:
        #     self.upload_blob(historical_value, file_name)
        # else:
        #     df0 = self.download_blob(file_name)
        #     self.upload_blob(pd.concat([historical_value,df0]).drop_duplicates(subset = 'portfolio_date'), file_name)

    def update_finno_sec_com(self):
        finno_api = finnomenaAPI(email=self.usr_pass['finnomena']['usr'], password=self.usr_pass['finnomena']['password'])
        _, _, compositions = finno_api.get_port_status("DIY")
        portfolio_date = compositions['portfolio_date'][0]
        compositions = compositions[['sec_name','nav_date', 'market_value', 'weight', 'return', 'cost', 'total_unit', 'avg_price', 'current_nav']]
        compositions = compositions.set_index('sec_name')
        columns = []
        for i in compositions.index:
            for j in compositions.columns:
                columns.append((i,j))
        
        #print(compositions.values.flatten())

        compositions = pd.DataFrame([compositions.values.flatten()], columns=columns)
        compositions.columns = pd.MultiIndex.from_tuples(compositions.columns, names=['sec_name','attributes'])
        compositions.index = [portfolio_date]

        self.update_file(compositions, self.finno_compo_csv, header=[0,1])
        # file_name = self.finno_compo_csv
        # if file_name not in self.blobs:
        #     self.upload_blob(compositions, file_name)
        # else:
        #     df0 = self.download_blob(file_name)
        #     self.upload_blob(pd.concat([df0,compositions]).drop_duplicates(), file_name)
        
        # return compositions
    
    def test_update(self):
        now = datetime.now()
        # dd/mm/YY H:M:S
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        df = pd.DataFrame([dt_string])

        self.update_file(df, 'test.csv')

# usr_pass = load_yaml('config/usr_pass.yaml')
# update_csv = update_csv(usr_pass)
# print(update_csv.update_sec_com())

# storage_client = storage.Client.from_service_account_json('gcs_cred/portfolio-dashboard-poch-94911bb96450.json')
# bucket = storage_client.get_bucket('portfolio-dashboard-poch.appspot.com')
# blob = bucket.blob('historical_proce.csv')
# downloaded_blob = blob.download_as_bytes()
# s=str(downloaded_blob,'utf-8')
# data = StringIO(s) 
# df=pd.read_csv(data)
# print(df)


#df = pd.read_csv('gs://portfolio-dashboard-poch.appspot.com/historical_price.csv')