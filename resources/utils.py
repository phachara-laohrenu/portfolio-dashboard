import yaml
from datetime import datetime
from dateutil import relativedelta
import pandas as pd
from io import StringIO
import os
from dateutil.parser import parse
from dateutil.rrule import rrule, DAILY, MO, TU, WE, TH, FR, SA, SU

def load_yaml(path: str):
    with open(path) as file:
        yaml_dict = yaml.load(file, Loader=yaml.FullLoader)
    return yaml_dict

def download_blob(storage_client, bucket_name, blob_name, header=0):
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    downloaded_blob = blob.download_as_bytes()

    filename, file_extension = os.path.splitext(blob_name)

    if file_extension == '.csv':
        s = str(downloaded_blob,'utf-8')
        data = StringIO(s) 
        out = pd.read_csv(data, index_col=0, header = header)

    elif file_extension == '.yaml':
        out = yaml.load(downloaded_blob)
    
    else:
        raise ValueError("Invalid file type: " + file_extension)

    return out

def get_key(mydict, value):
    return list(mydict.keys())[list(mydict.values()).index(value)]

def monthname2num(month_name):
    month_name = month_name.lower()
    month_name_dict = {'january':1,'febuary':2,'march':3,'april':4,'may':5,'june':6,
                       'july':7,'august':8,'september':9,'october':10,'november':11,'december':12}
    month_name_dict_abb = {}
    for key, val in month_name_dict.items():
        month_name_dict_abb[key[:3]] = val
    month_name_dict = {**month_name_dict,**month_name_dict_abb}
    
    return month_name_dict[month_name]

def get_start_date(time_range: str, splitter = '-'):
        """
        Arg
        time_range: e.g. 1M, 5M, 1Y, 10Y, MAX

        Return
        start_date in 'yyyy-mm-dd'
        """

        time_range = time_range.lower()
        if time_range != 'max':
            number = int(time_range[:-1])
            unit = time_range[-1]
            if unit == 'y':
                number *= 12
        
            n = datetime.now()
            n = n - relativedelta.relativedelta(days=1)
            n = n - relativedelta.relativedelta(months=number)
            dateStr = n.strftime(splitter.join(['%Y','%m','%d']))
        elif time_range == 'max':
            dateStr = splitter.join(['1970','01','01'])
        else:
            raise Exception("Invalid time_range: " + time_range)
        
        return dateStr

def get_asset_from_info(info: str, info_val = None, assets_path = 'config/assets.yaml'):
    assets_dict = load_yaml(assets_path)['asset_library']
    masterfunds_dict = assets_dict['master_funds']
    info_dict = {v[info]:k for k,v in masterfunds_dict.items()}

    if info_val is not None:
        asset_name = info_dict[info_val]
    else:
        asset_name = None

    return info_dict, asset_name

def get_assetType(asset_name: str = None, assets_path = 'config/assets.yaml'):
    assets_dict = load_yaml(assets_path)['asset_library']
    type_dict = {}
    for asset_type, assets in assets_dict.items():
        for asset in assets:
            type_dict[asset] = asset_type

    if asset_name is not None:
        asset_type = type_dict[asset_name]
    else:
        asset_type = None
    
    return type_dict, asset_type

def get_assetinfotable(assets_path = 'config/assets.yaml'):
    assets_dict = load_yaml(assets_path)['asset_library']
    info_dict = {'asset_name':[], 'asset_type':[]}
    for asset_type, assets in assets_dict.items():
        for asset_name, info in assets.items():
            info_dict['asset_name'].append(asset_name)
            info_dict['asset_type'].append(asset_type)
            for att, att_val in info.items():
                # create new attribute if not exist
                if att not in info_dict:
                    info_dict[att] = []
                # fill new attribute with None 
                n_assets = len(info_dict['asset_name'])
                n_att = len(info_dict[att])
                info_dict[att] += [None]*(n_assets-n_att-1)
                info_dict[att].append(att_val)
            
            # Check for any existing attributes that has not been update 
            for att, att_val in info_dict.items():
                info_dict[att] += [None]*(n_assets-len(att_val))

    df = pd.DataFrame(info_dict)
    df.set_index("asset_name", inplace=True)
    return df

def get_dates(start_date, end_date=None):
    if end_date is None:
        end_date=datetime.now().strftime('%Y-%m-%d')
    result = rrule(
    DAILY,
    byweekday=(MO,TU,WE,TH,FR),
    dtstart=parse(start_date),
    until=parse(end_date)
    )
    dates_list = [n.strftime('%Y-%m-%d') for n in result]
    return dates_list

def remove_weekends(time_series):
    """
    time_series: dataframe of an asset price with date as index
    """
    end_date=datetime.now().strftime('%Y-%m-%d')
    start_date = time_series.index.values[0]
    result = rrule(
    DAILY,
    byweekday=(SA,SU),
    dtstart=parse(start_date),
    until=parse(end_date)
    )
    weekend_list = [n.strftime('%Y-%m-%d') for n in result]
    date_list = time_series.index.values
    drop_dates = list(set(weekend_list) & set(date_list))
    
    time_series = time_series.drop(drop_dates)

    return time_series


                
    