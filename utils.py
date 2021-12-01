import plotly.express as px
import pandas as pd
import datetime
import numpy as np

def proba_gantt(df, file_path=None):
    """
    file_path : allows to save plotly chart to html file
    """
    df_box = (pd.melt(df, id_vars=['Task', 'Simu'], value_vars=['Start', 'Finish'])
                .set_index(["Task", "Simu"], drop=False)
                .sort_index())
    trace_box = px.box(df_box, x="value", y="Task", color="variable", orientation="h", boxmode="group")#, points="all")
    #trace_box = px.violin(df_box, x="value", y="Task", color="variable", orientation="h", box=True, violinmode="group")#, meanline_visible=True)#, points="all")
    #trace_box.update_xaxes(tickangle = 90)

    df_gantt = (pd.melt(df, id_vars=['Task', 'Simu'], value_vars=['Start', 'Finish'])
                .drop("Simu", axis=1)
                .groupby(["Task", "variable"])
                .mean(numeric_only=False)
                .unstack(level=-1)
                .droplevel(0,axis=1))
    df_gantt["Task"] = df_gantt.index
    trace_gantt = px.timeline(df_gantt, x_start="Start", x_end="Finish", y="Task", opacity=0.5)
    #fig.add_trace(trace_box)#, row=1, col=1)
    fig = trace_gantt
    for trace in trace_box.data:
        fig.add_trace(trace)
        
    if file_path is not None:
        # https://plotly.com/python/interactive-html-export/
        fig.write_html(file_path)

    #fig.show()
    return fig
    
#proba_gantt(df)    

def simulation_to_df(file, filter=None):
    """Reads wait and sea output file and converts it into a pandas dataframe usable with proba_gantt
    
    filter : tuple (lower, upper), allows to filter between two PXX eg (0.875, 0.925) or (0.9, 1) """
    
    df_start = pd.read_excel(file, sheet_name="raw start dates", index_col=0)
    df_end = pd.read_excel(file, sheet_name="raw end dates", index_col=0)
    df_durations = pd.read_excel(file, sheet_name="raw gross durations", index_col=0)
    df_standby = pd.read_excel(file, sheet_name="raw standby", index_col=0)
    
    df_simulation = pd.DataFrame()
    df_simulation["Start"] = pd.to_datetime(df_start.stack())
    df_simulation["Finish"] = pd.to_datetime(df_end.stack())
    df_simulation["Gross Durations"] = df_durations.stack()
    df_simulation["Standby"] = df_standby.stack()
    df_simulation.index = df_simulation.index.set_names(["Task", "Simu"])
    df_simulation = df_simulation.reset_index()
    # https://stackoverflow.com/questions/20110170/turn-pandas-multi-index-into-column
    
    if filter is not None:
        lower = df_simulation.quantile(filter[0]).Standby
        upper = df_simulation.quantile(filter[1]).Standby

        df_simulation = df_simulation[(df_simulation.Standby >= lower) & (df_simulation.Standby <= upper)]
    
    return df_simulation