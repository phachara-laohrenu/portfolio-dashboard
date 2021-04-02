import streamlit as st
import pandas as pd
from google.cloud import storage

from resources.myport import MyPortfolio
from resources.plot_graph import plot_port_return, plot_port_compo
from resources.analyser import Analyser

import time

port = MyPortfolio()

t0 = time.time()
#port_status = port.get_status()
#print(time.time()-t0)
port_status_ts = port.get_finno_status_ts()
print(time.time()-t0)
port_compo = port.get_finno_compo()
print(time.time()-t0)

# st.write(pd.DataFrame([port_status], columns=port_status.keys()))


# --------------------------------------------------------------------------------
# Streamlit Interface
# --------------------------------------------------------------------------------
st.title("Portfolio Dashboard")

# Last update ----------------
update_log = port.get_update_log()
if update_log is None:
    st.text('last update at: have not updated')
else:
    st.text('last update at: ' + update_log.iloc[-1,0])

# update button ------------------
update = st.button('update')
if update:
    port.update()

# line chart of port return
port_status_ts['return'] = 100*(port_status_ts['value'] - port_status_ts['cost'])/port_status_ts['cost']
st.write(plot_port_return(port_status_ts))

# pie chart of current portfolio composition
st.write(plot_port_compo(port_compo))

# analyse
port_assets = list(port_compo.columns.get_level_values(0).unique())
print(port_assets)
analyser = Analyser(port_assets)
st.write(analyser.time_series_df)
corelation = analyser.analyse()
st.write(corelation)

#st.line_chart(port_status_ts)

