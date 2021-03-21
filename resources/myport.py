from finnomena_api import finnomenaAPI
from google.cloud import storage
import os

from resources.update_csv import UpdateCSV
from resources.utils import load_yaml, download_blob

class MyPortfolio():

    def __init__(self, bucket_name='portfolio-dashboard-poch.appspot.com'):
        
        self.storage_client = storage.Client()
        self.bucket_name = bucket_name

        self.usr_pass = download_blob(self.storage_client, self.bucket_name, 'usr_pass.yaml')
        self.finno_api = finnomenaAPI(email=self.usr_pass['finnomena']['usr'], 
                        password=self.usr_pass['finnomena']['password'])

        self.file_name_dict = load_yaml('config/keys.yaml')['file_name']


        self.update_csv = UpdateCSV(self.usr_pass)
    
    def update(self):
        self.update_csv.update_finno_port()
        self.update_csv.update_finno_sec_com()
        self.update_csv.update_log()

    def get_status(self):
        # finnomena
        finno_port_status, _, _ = self.finno_api.get_port_status("DIY")

        port_status = finno_port_status

        return port_status
    
    def get_finno_status_ts(self):
        file_name = self.file_name_dict['finno_port_status']
        # check if file exists
        if file_name in self.update_csv.blobs:
            df = download_blob(self.storage_client, self.bucket_name, file_name)
        else:
            df = None
        return df 
    
    def get_finno_compo(self):
        file_name = self.file_name_dict['finno_port_compo']
        # check if file exists
        if file_name in self.update_csv.blobs:
            df = download_blob(self.storage_client, self.bucket_name, file_name, header=[0,1])
        else:
            df = None
        return df 

    def get_update_log(self):
        file_name = self.file_name_dict['update_log']
        # check if file exists
        if file_name in self.update_csv.blobs:
            df = download_blob(self.storage_client, self.bucket_name, file_name)
        else:
            df = None
        return df