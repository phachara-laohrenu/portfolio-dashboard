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
st.line_chart(port_status_ts['value'])
submit = st.button('refresh')

st.write(test_csv)

if submit:
    port.update()
    # #upload_blob('portfolio-dashboard-poch.appspot.com', 'data/historical_price.csv', 'historical_proce.csv')
    # df = pd.read_csv('gs://portfolio-dashboard-poch.appspot.com/historical_price.csv')
    # st.write(df)
    # #requests.post('http://127.0.0.1:8000/letters', json=new_candidates)