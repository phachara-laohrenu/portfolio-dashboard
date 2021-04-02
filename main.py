from resources.myport import MyPortfolio
from resources.update_csv import UpdateCSV


def update_port(event, context):
    # update port
    port = MyPortfolio()
    port.update()

    # update feeder
    updater = UpdateCSV()
    _, _, compositions = updater.finno_api.get_port_status("DIY")
    secs = list(compositions['sec_name'])
    updater.update_feeder(secs)
