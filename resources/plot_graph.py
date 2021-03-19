import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd

def plot_port_return(port_status_ts):
    port_status_ts = port_status_ts.sort_index()
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(x=port_status_ts.index, y=port_status_ts['return'], name="return"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=port_status_ts.index, y=port_status_ts['value'], name="value"),
        secondary_y=True,
    )

    # Add figure title
    fig.update_layout(
        title_text="Portfolio return and and value"
    )

    # Set y-axes titles
    fig.update_yaxes(title_text="return [%]", secondary_y=False)
    fig.update_yaxes(title_text="value [THB]", secondary_y=True)

    return fig

def plot_port_compo(compo):
    last_compo = compo.iloc[-1]
    sec_names = list(set(last_compo.index.get_level_values(0)))
    attributes = list(last_compo[sec_names[0]].index)
    l = []
    for i in sec_names:
        tmt = last_compo[i]
        l.append(list(tmt.values))

    last_compo = pd.DataFrame(l,index=sec_names, columns=attributes)

    fig = px.pie(last_compo, values='market_value', names=last_compo.index, title='Portfolio Composition')
    
    return fig
