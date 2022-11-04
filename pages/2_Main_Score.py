import streamlit as st
import pandas as pd
import numpy as np
import json
import geopandas as gpd
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
def combined_dashboard(callsigns,tab):
    st.write("IN-Progress")
  #  command_master="Select Contest_Call, points*mults AS total_score,count(Q) as QSOs, sum(points) as Points, sum(mults) as Mults FROM qsos"
  #  score_frame=pd.read_sql(command_master,,)
    # Summed QSO Activity by Band
    # Table - Score, Callsign, Place, Active, Radio 1 Data
    # Map of active contesters - Home Lat. Long

    combined_table= pd.DataFrame(
        columns=["Active","Callsign","Score","Place","Radio1"]
    )
    with tab:
        st.dataframe(combined_table)