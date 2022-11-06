import streamlit as st
import pandas as pd
import numpy as np
import json
import geopandas as gpd
import sqlalchemy
import dashboard_defaults as dash
import leafmap.foliumap as leafmap
# import mysql.connector
st.set_page_config(layout="wide")
    
# def init_connection():
#     return mysql.connector.connect(**st.secrets["mysql"])

# def run_query(query):
#     with conn.cursor() as cur:
#         cur.execute(query)
#         return cur.fetchall()

# Writing and porting data
@st.experimental_memo
def combined_dashboard(callsigns):
    st.write("IN-Progress")
  #  command_master="Select Contest_Call, points*mults AS total_score,count(Q) as QSOs, sum(points) as Points, sum(mults) as Mults FROM qsos"
  #  score_frame=pd.read_sql(command_master,,)
    # Summed QSO Activity by Band
    # Table - Score, Callsign, Place, Active, Radio 1 Data
    # Map of active contesters - Home Lat. Long
    connection=dash.connect()
    query="SELECT * FROM last_qsos;"
    qso_frame=pd.read_sql(sql=query,con=connection)
   
    map_query="Select * from home;"
    map_stations=dash.run_query(connection,map_query)
    base_map = leafmap.Map(draw_export=True)
    base_layer = dash.geo_map(base_map)
    stationmap= dash.to_geojson(base_map,df=map_stations,lat1='lat',lon1='lon',lat2=None, lon2=None,properties=[
        'Contest_Call','classification'
    ],geo_type='Point')
    base_map.add_gdf(base_layer, layer_name="ARRL Sections")
    base_map.add_gdf(stationmap, layer_name="Stations")
    base_map.set_center(-97,38,3.5)
    base_map.to_streamlit()
    st.write(map_stations)
    st.dataframe(qso_frame)
   # command_calc="Select JSON_ONJECT(c.Last_Run_QSO_TIme, c.Last_Run_QSO_Time, c.Last_SP_QSO_Time, c.Last_SP_QSO, c.Top_OP_Mults, c.Top_OP_Score FROM calculated AS c WHERE c.Contest_Call="+callsign+"ORDER BY c.timestamp DESC LIMIT 1;"
    
 
    combined_table= pd.DataFrame(
        columns=["Active","Callsign","Score","Place","Radio1"]
    )
    st.dataframe(combined_table)

combined_dashboard(["K9CT"])