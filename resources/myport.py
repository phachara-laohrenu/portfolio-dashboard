from finnomena_api import finnomenaAPI
from google.cloud import storage
import os

from resources.update_csv import UpdateCSV
from resources.utils import load_yaml, download_blob_csv

class MyPortfolio():

    def __init__(self, credential_folder = 'gcs_cred', bucket_name='portfolio-dashboard-poch.appspot.com'):
        self.usr_pass = load_yaml('config/usr_pass.yaml')
        self.finno_api = finnomenaAPI(email=self.usr_pass['finnomena']['usr'], 
                        password=self.usr_pass['finnomena']['password'])

        self.credential_path = credential_folder + '/' + os.listdir(credential_folder)[0]
        self.storage_client = storage.Client.from_service_account_json(self.credential_path)
        self.bucket_name = bucket_name

        self.finno_port_csv = 'finno_port_status.csv'
        self.finno_compo_csv = 'finno_port_compo.csv'

        # login
        self.finno_api.login()
    
    def update(self):
        update_csv = UpdateCSV(self.usr_pass)
        # update_csv.update_finno_port()
        # update_csv.update_finno_sec_com()
        update_csv.test_update()

    def get_status(self):
        
        # finnomena
        finno_port_status, _, _ = self.finno_api.get_port_status("DIY")

        port_status = finno_port_status

        return port_status
    
    def get_finno_status_ts(self):
        df = download_blob_csv(self.storage_client, self.bucket_name, self.finno_port_csv)
        return df 
    
    def get_finno_compo(self):
        df = download_blob_csv(self.storage_client, self.bucket_name, self.finno_compo_csv, header=[0,1])
        return df 

    def get_test(self):
        df = download_blob_csv(self.storage_client, self.bucket_name, 'test.csv')
        return df