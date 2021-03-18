import streamlit as st
import pandas as pd
from google.cloud import storage

from resources.myport import MyPortfolio


port = MyPortfolio()

port_status = port.get_status()
port_status_ts = port.get_finno_status_ts()
port_compo = port.get_finno_compo()
test_csv = port.get_test()
# st.write(pd.DataFrame([port_status], columns=port_status.keys()))


# --------------------------------------------------------------------------------
# Streamlit Interface
# --------------------------------------------------------------------------------
st.title("Portfolio Dashboard")

update_log = port.get_update_log()
if update_log is None:
    st.text(port.get_update_log())
else:
    st.text('last update at: ' + update_log.iloc[-1,0])

st.line_chart(port_status_ts['value'])
refresh = st.button('refresh')

st.write(test_csv)

if refresh:
    port.update()