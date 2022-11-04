import streamlit as st 
import geopandas as gpd
import geojson, json
import pandas as pd
import numpy as np
import pydeck as pdk
import leafmap.foliumap as leafmap
import mysql.connector
st.set_page_config(layout="wide")
with open("frontend/css/streamlit.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
@st.experimental_memo()
def geo_map(map_color):
    width = 1250
    height=550
    file_path = r"ARRL_Sections.geojson"
    layer_name = "ARRL_Sections"
    gdf = gpd.read_file(file_path)
    lon, lat = leafmap.gdf_centroid(gdf)
           
    m = leafmap.Map(draw_export=True)
    m.add_gdf(gdf, layer_name=layer_name)
    m.set_center(-97,38,3.5)
    m.to_streamlit(width=width, height=height)
def select_individual_data(callsign):
    connection= mysql.connoector.connect()
    command_calc="Select JSON_ONJECT(c.Last_Run_QSO_TIme, c.Last_Run_QSO_Time, c.Last_SP_QSO_Time, c.Last_SP_QSO, c.Top_OP_Mults, c.Top_OP_Score FROM calculated AS c WHERE c.Contest_Call="+callsign+"ORDER BY c.timestamp DESC LIMIT 1;"
    command_radio="SELECT r.Radio_1_Operator, r.Radio_1_Mode, r.Radio_1_Freq, r.Radio_1_Status, r.Radio_1_Macro, r.Radio_1_TX, r.Radio_1_Focus, r.Radio_1_Rate, r.Radio_2_Operator, r.Radio_2_Mode, r.Radio_2_Freq, r.Radio_2_Status, r.Radio_2_Macro, r.Radio_2_TX, r.Radio_2_Focus, r.Radio_2_Rate FROM radio AS r WHERE r.Contest_Call="+callsign+"ORDER BY r.timestamp DESC LIMIT 1;" 
    command_score="SELECT  s.Total_Score, s.Total_QSOs, s.Total_Points, s.Total_Mults, s.Current_Total_Rate FROM score AS s WHERE s.Contest_Call="+callsign+"ORDER BY s.timestamp DESC LIMIT 1;"
    command_q="SELECT q.Last_QSO,q.Last_QSO_Band, q.Last_QSO_Mode, q.Last_QSO_Exchange, q.Last_QSO_Distance, q.Last_QSO_OP FROM qsos as q where q.Contest_Call="+callsign+"ORDER BY q.timestamp DESC LIMIT 1;"
callsigns = ["K9CT","KD9LSV","AA0Z","N0AX","W0ECC","KD9WHO"]
with st.sidebar:
    #callsigns = run_query("SELECT DISTINCT callsign FROM home_table ORDER BY callsign ASC;")
    chosen_callsign=st.selectbox('Choose Callsign',callsigns)
## Choices Defaults
if (chosen_callsign=="K9CT"):
    payload_test= {"Last_Run_QSO_Time":"00:20:00","Last_Run_QSO":"KD9LSV","Last_SP_QSO_Time":"00:05:02","Last_SP_QSO":"WT2P","Top_OP_Mults":"K9CT","Radio_1_Operator":"AA0Z","Radio_1_Mode":"Run","Radio_1_Freq":"21245.4","Radio_1_Status":"","Radio_1_Macro":"","Radio_1_TX":"","Radio_1_Focus":"","Radio_1_Rate":250,"Radio_2_Operator":"AB9YC","Radio_2_Mode":"S&P","Radio_2_Freq":"21295.7","Radio_2_Status":"","Radio_2_Macro":"","Radio_2_TX":"","Radio_2_Focus":"","Radio_2_Rate":60,"Total_Score":2534136,"Total_QSOs":2245,"Total_Points":1914,"Total_Mults":1324,"Current_Total_Rate":125,"Top_OP_Score":"AB9YC","Last_QSO":"K1AR","Last_QSO_Band":"20M","Last_QSO_Mode":"PH","Last_QSO_Exchange":"5","Last_QSO_Distance":"1503 Mi","Last_QSO_OP":"AB9YC"}
    payload=payload_test
else:
    payload_test_2= {"Last_Run_QSO_Time":"00:20:00","Last_Run_QSO":"KO4AFL","Last_SP_QSO_Time":"00:05:02","Last_SP_QSO":"WT9P","Top_OP_Mults":"K9UR","Radio_1_Operator":"WB0SND","Radio_1_Mode":"Run","Radio_1_Freq":"14245.4","Radio_1_Status":"","Radio_1_Macro":"","Radio_1_TX":"","Radio_1_Focus":"","Radio_1_Rate":125,"Radio_2_Operator":"WZ0W","Radio_2_Mode":"S&P","Radio_2_Freq":"14279.7","Radio_2_Status":"","Radio_2_Macro":"","Radio_2_TX":"","Radio_2_Focus":"","Radio_2_Rate":100,"Total_Score":1121736,"Total_QSOs":1445,"Total_Points":1214,"Total_Mults":924,"Current_Total_Rate":80,"Top_OP_Score":"N0AX","Last_QSO":"N3MM","Last_QSO_Band":"40M","Last_QSO_Mode":"PH","Last_QSO_Exchange":"4","Last_QSO_Distance":"2503 Mi","Last_QSO_OP":"N0AX"}
    payload=payload_test_2
### End_Defaults

#payload=select_individual_data(chosen_callsign)

col_LastQSO, col_CurrentQSO, col_Score = st.columns([.9,5,1])
with col_LastQSO:
    st.markdown("## Last QSO's")
    st.metric("Last Run QSO",payload["Last_Run_QSO_Time"])
    st.metric("Last Run QSO",payload["Last_Run_QSO"])
    st.metric("Last S&P QSO",payload["Last_SP_QSO_Time"])
    st.metric("Last Run QSO",payload["Last_SP_QSO"])
    st.metric("Top OP Mults",payload["Top_OP_Mults"])   
with col_CurrentQSO:

    st.markdown("<h2><center> QSO Map </center></h2>",unsafe_allow_html=True) 
    map_color=[150,79,24,183]
    geo_map(map_color)       
with col_Score:
    st.markdown("## Score")
    st.metric("Total Score",payload["Total_Score"])
    st.metric("QSO's",payload["Total_QSOs"])
    st.metric("Points",payload["Total_Points"])
    st.metric("Mults",payload["Total_Mults"])
    st.metric("Current Total QSO Rate",payload["Current_Total_Rate"])
    st.metric("Top OP Score",payload["Top_OP_Score"]) 
with st.container():
    col_space_a, col_Last, col_Last_QSO,col_band,col_mode,col_exchange,col_distance,col_op, col_Score_b = st.columns([1.75,1,.7,.7,.5,.7,.7,.7,1.5])
    with col_Last:
        st.markdown("## Latest QSO:")
    with col_Last_QSO:
        st.metric("Last QSO",payload["Last_QSO"])
    with col_band:
        st.metric("Band",payload["Last_QSO_Band"])
    with col_mode:
        st.metric("Mode",payload["Last_QSO_Mode"])
    with col_exchange:
        st.metric("Exchange",payload["Last_QSO_Exchange"])
    with col_distance:
        st.metric("Distance",payload["Last_QSO_Distance"])
    with col_op:
        st.metric("OP",payload["Last_QSO_OP"])
    with col_Score_b:
        st.empty()
with st.container():
    col_1_title, col_2_title= st.columns([1,1])
    with col_1_title:
        st.title("Radio 1 Data")
    with col_2_title:
        st.title("Radio 2 Data")
    col_1,col_2,col_3,col_4,col_5,col_6,col_7,col_1_2,col_2_2,col_3_2,col_4_2,col_5_2,col_6_2,col_7_2= st.columns([3,2,3,2,2,2,2,3,2,3,2,2,2,2]) 
    #Radio1
    with col_1:
        st.metric("Operator",payload["Radio_1_Operator"])
    with col_2:
        st.metric("Mode",payload["Radio_1_Mode"])
    with col_3:
        st.metric("Freq",payload["Radio_1_Freq"])
    with col_4:
        st.metric("Status",payload["Radio_1_Status"])
    with col_5:
        st.metric("Macro",payload["Radio_1_Macro"])
    with col_6:
        st.metric("Radio 1 Rate",payload["Radio_1_Rate"])
    with col_7:
        st.markdown("TX and Focus")
    # Radio 2
    with col_1_2:
        st.metric("Operator",payload["Radio_2_Operator"])
    with col_2_2:
        st.metric("Mode",payload["Radio_2_Mode"])
    with col_3_2:
        st.metric("Freq",payload["Radio_2_Freq"])
    with col_4_2:
        st.metric("Status",payload["Radio_2_Status"])
    with col_5_2:
        st.metric("Macro",payload["Radio_2_Macro"])
    with col_6_2:
        st.metric("Radio 2 Rate",payload["Radio_2_Rate"])
    with col_7_2:
        st.markdown("TX and Focus")