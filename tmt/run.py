from utils import load_yaml
from retriever import Retriever

# config = load_yaml('config.yaml')
# keys = load_yaml('keys.yaml')

retriever = Retriever()
# data = []

# df = retriever.get('MAX', 'F0GBR04AOC]2]0]FOGBR$$ALL')
df = retriever.get_current('MAX')
#df = retriever.get('financialtimes', 'MAX', asset_name='UBS (Lux) Equity Fund - China Opprtunity (USD) I-A1-acc')
print(df)
df.to_csv('data/historical_price.csv')
#print(list(config['selected_asset']['morningstar'].keys()))
