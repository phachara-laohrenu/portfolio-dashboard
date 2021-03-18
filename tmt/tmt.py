import investpy
import pandas as pd 
# df = investpy.get_fund_recent_data(fund='Allianz Global Investors Fund - Allianz Global Artificial Intelligence',
#                                    country='luxembourg')
# print(df.head())


# search_result = investpy.search_funds(by='name', value='Digital Health Equity Fund')
# #print(search_result.loc[0]['name'])

# df = investpy.get_funds()
# print(df[df['symbol']=='0P0001C6GE'])

storage_url = 'https://console.cloud.google.com/storage/browser/portfolio-dashboard-poch.appspot.com'

df = pd.read_csv('data/historical_price.csv')

