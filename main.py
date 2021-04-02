from resources.myport import MyPortfolio
from resources.update_csv import UpdateCSV
from finnomena_api import finnomenaAPI

def update_port(event, context):
    # update port
    port = MyPortfolio()
    port.update()


