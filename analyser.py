import pandas as pd
import numpy as np
import scipy 

historical_price = pd.read_csv('data/historical_price.csv', index_col = 0)


# get first row where every assets have price
inception_dates = {}
for i,col in enumerate(historical_price.columns):
    inception_date = historical_price.iloc[:,i].first_valid_index()
    inception_dates[col] = inception_date

# foward fill missing value
historical_price = historical_price.ffill()

# calculate return
historical_return = (historical_price - historical_price.shift(1))/historical_price.shift(1)

# calculate correlation
correlation = historical_return.corr()

# calculate covariance
covariance = historical_return.cov()




