from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import requests
import plotly as pl
import plotly.express as px
from dash import Dash, dcc, html, dash_table, Input, Output
import dash
from dash import dash_table

df= pd.read_excel("unificado.xlsx")
df

#construir dashboard
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server=app.server

app.title="Dashboard"

cuentas=["Inflacion","Remesas", "Emision"]

#layout del app
app.layout = html.Div([
    html.Div([html.Div([
        
    #primer drop down para elegir las empresas
    html.Div(dcc.Dropdown(
    id="inflaciondd",value=["2015","2016","2017","2018","2019","2020","2021","2022","2023"],clearable=False, multi=True,
    options=[{'label':x,'value':x} for x in sorted(df.Año.unique())]
    ),className="six columns", style={"width":"50%"},),
    
    #revisar
    html.Div(dcc.Dropdown(
    id="indicador_indd",value="Inflacion",clearable=False,
    options=[{'label':x,'value':x} for x in cuentas]
    ), className="six columns"), 
    ], className="row"),],className="custom-dropdown"),
    
    #graficas
    html.Div([dcc.Graph(id="graph",figure={},config={"displayModeBar":True,"displaylogo":False,
                                                   #"modeBarButtonsToRemove":['pan2d','lasso2d',
                                                   #                         'select2d']
                                                    }),],style={'width':'1100px'}),
    html.Div([dcc.Graph(id="boxplot",figure={},)],style={"width":'1100px'}),
    
    html.Div([dcc.Graph(id="pie",figure={},)],style={"width":'1100px'}),
    
    #tabla
    html.Div(html.Div(id="table-container"),style={'marginBottom':'15px','marginTop':
                                                 "10px"}),])


#callback de la funcion
@app.callback(
    [Output(component_id="graph",component_property="figure"),
    Output(component_id="boxplot",component_property="figure"),
    Output(component_id="pie",component_property="figure"),
    Output("table-container",'children')],
    [Input(component_id="inflaciondd",component_property="value"),
    Input(component_id="indicador_indd",component_property="value")]
)

#definicion de la funcion

def display_value(selected_company,selected_account):
    if len(selected_company)==0:
        df2=df[df["Año"].isin(["2015","2016","2017","2018","2019","2020","2021","2022","2023"])]
    else:
        df2=df[df["Año"].isin(selected_company)]
        
    
    #grafica1
    fig= px.line(df2,color="Año",x="Mes",markers=True,y=selected_account,
                width=1000,height=500)
    
    fig.update_layout(title=f'{selected_account} de {selected_company}',
                     xaxis_title="Meses",)
    fig.update_traces(line=dict(width=2))
    
    #grafica 2
    fig2=px.box(df2,color="Año",x="Año",y=selected_account,
               width=1000,height=500)
    fig2.update_layout(title=f'{selected_account} de {selected_company}',
                      )
    
    #grafica 3
    fig3= px.pie(df2, names="Año", values=selected_account, width=1000, height=500)
    fig3.update_traces(title=f'Representación anual de la {selected_account} total del periodo {selected_company}')
    
    #modificar data frame para poder hacerlo tabla
    df_reshaped = df2.pivot(index='Año', columns='Mes', values=selected_account)
    df_reshaped_2 = df_reshaped.reset_index()

    #tabla
    return (fig,fig2,fig3,
           dash_table.DataTable(columns=[{"name":i,"id":i} for i in df_reshaped_2],
                               data=df_reshaped_2.to_dict("records"),
                               export_format="csv",#para guardar como csv
                               fill_width=True,
                               style_header={'backgroundColor':'blue',
                                            'color':'white'},
                               ))
#setear server y correr:

if __name__ == '__main__':
    app.run_server(debug=False,host="0.0.0.0",port=10000)
