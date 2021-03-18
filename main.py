from resources.myport import MyPortfolio


def update_port(event, context):
    port = MyPortfolio()
    port.update()