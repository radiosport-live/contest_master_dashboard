import streamlit as st 
import geopandas as gpd
import geojson, json
import pandas as pd
import numpy as np
import dashboard_default as dash
import leafmap.foliumap as leafmap
def qso_line_map(_m, con, callsign, group, time):
    base_command = "SELECT q.mycall as 'Own Call', h.lat AS 'latfrom', h.lon as 'lonfrom',q.external_Call as 'Contact Call',CONVERT(q.lat,FLOAT) as 'latto', CONVERT(q.lon,FLOAT) as 'lonto',TIMESTAMPDIFF(MINUTE,NOW(),`timestamp`) as 'Time Elapsed', `timestamp` FROM qsos as q INNER JOIN home as h ON h.Contest_Call=q.mycall WHERE ABS(TIMESTAMPDIFF(MINUTE,NOW(),`timestamp`)) <="+str(time)
    # allow all QSOS or only one callsign
    if (group.upper == 'Y'):
        base_command += " ORDER BY `timestamp` DESC;"
    else:
        base_command += " and q.mycall=\""+callsign+"\" ORDER BY `timestamp` DESC;"
    map=dash.run_query(dash.connect(),base_command)
    map['timestamp']=map['timestamp'].astype(str)
    spokemap= dash.to_geojson(_m,df=map,lat1='latfrom',lon1='lonfrom',lat2='latto',lon2='lonto',properties=[
        'Own Call','Contact Call'
    ],geo_type='LINESTRING')
    return spokemap
def app():
    st.set_page_config(layout="wide")
    #callsigns = ["K9CT","KD9LSV","AA0Z","N0AX","W0ECC","KD9WHO"]
    callsigns = dash.run_query(dash.connect(),"SELECT DISTINCT Contest_Call FROM home ORDER BY Contest_Call ASC;")
    with st.sidebar:
        chosen_callsign=st.selectbox('Choose Callsign',callsigns)
    with open("frontend/css/streamlit.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    # Payload SQL Commands
    st.write(dash.run_query(dash.connect(),"SELECT * from qsos limit 1;"))
    command_run= "SELECT * from last_qsos where `Contest Call` ="+chosen_callsign+";"
    command_calc="Select JSON_ONJECT(c.Top_OP_Mults, c.Top_OP_Score FROM calculated AS c WHERE c.Contest_Call="+chosen_callsign+"ORDER BY c.timestamp DESC LIMIT 1;"
    command_radio1="SELECT r.OpCall, r.IsRunning, r.Freq, r.Status, r.Macro, r.IsTransmitting, r.FocusRadioNr, r.Radio_2_Rate from radio AS r WHERE r.Contest_Call="+chosen_callsign+" and r.radio_station=1 ORDER BY r.timestamp DESC Limit 1;" 
    command_radio2="SELECT r.OpCall, r.IsRunning, r.Freq, r.Status, r.Macro, r.IsTransmitting, r.FocusRadioNr, r.Radio_2_Rate from radio AS r WHERE r.Contest_Call="+chosen_callsign+" and r.radio_station=2 ORDER BY r.timestamp DESC Limit 1;"
    command_score="SELECT  s.Total_Score, s.Total_QSOs, s.Total_Points, s.Total_Mults, s.Current_Total_Rate FROM score AS s WHERE s.Contest_Call="+chosen_callsign+"ORDER BY s.timestamp DESC LIMIT 1;"
    command_q="SELECT q.Last_Run_QSO_Time,q.Last_Run_QSO, q.Last_QSO_Band, q.Last_QSO_Mode, q., q.Last_QSO_Distance, q.Last_QSO_OP FROM last_qsos as q where q.`Contest Call`="+chosen_callsign+"ORDER BY q.timestamp DESC LIMIT 1;"
    # Sidebar Configuration
  
    # Payload Defaults
    payload_test= {"Last_Run_QSO_Time":"00:20:00","Last_Run_QSO":"KD9LSV","Last_SP_QSO_Time":"00:05:02","Last_SP_QSO":"WT2P","Top_OP_Mults":"K9CT","Radio_1_Operator":"AA0Z","Radio_1_Mode":"Run","Radio_1_Freq":"21245.4","Radio_1_Status":"","Radio_1_Macro":"","Radio_1_TX":"","Radio_1_Focus":"","Radio_1_Rate":250,"Radio_2_Operator":"AB9YC","Radio_2_Mode":"S&P","Radio_2_Freq":"21295.7","Radio_2_Status":"","Radio_2_Macro":"","Radio_2_TX":"","Radio_2_Focus":"","Radio_2_Rate":60,"Total_Score":2534136,"Total_QSOs":2245,"Total_Points":1914,"Total_Mults":1324,"Current_Total_Rate":125,"Top_OP_Score":"AB9YC","Last_QSO":"K1AR","Last_QSO_Band":"20M","Last_QSO_Mode":"PH","Last_QSO_Exchange":"5","Last_QSO_Distance":"1503 Mi","Last_QSO_OP":"AB9YC"}
    payload=payload_test
    ### End_Defaults

    #payload=select_individual_data(chosen_callsign)

    col_LastQSO, col_CurrentQSO, col_Score = st.columns([.9,5,1])
    # Last QSO Info
    with col_LastQSO:
        st.markdown("## Last QSO's")
        st.metric("Last Run QSO",payload["Last_Run_QSO_Time"])
        st.metric("Last Run QSO",payload["Last_Run_QSO"])
        st.metric("Last S&P QSO",payload["Last_SP_QSO_Time"])
        st.metric("Last Run QSO",payload["Last_SP_QSO"])
        st.metric("Top OP Mults",payload["Top_OP_Mults"])   
    # QSO Map
    with col_CurrentQSO:
        st.markdown("<h2><center> QSO Map </center></h2>",unsafe_allow_html=True) 
        base_map = leafmap.Map(draw_export=True)
        base_layer = dash.geo_map(base_map)
        qso_line_layer = qso_line_map(base_map,dash.connect(),chosen_callsign,"Y",59408) 
        #st.write(qso_line_layer)
        base_map.add_gdf(base_layer, layer_name="ARRL Sections")
        try:
            base_map.add_gdf(qso_line_layer, layer_name="QSOs")
        except IndexError:
            with st.sidebar:
               st.write("No Valid Layer")
        except:
            with st.sidebar:
                st.write("Error on QSO Layer")
        base_map.set_center(-97,38,3.5)
        base_map.to_streamlit(width=900, height=550)
        backup_map = leafmap.Map(draw_export=True)
    # Score Column
    with col_Score:
        st.markdown("## Score")
        st.metric("Total Score",payload["Total_Score"])
        st.metric("QSO's",payload["Total_QSOs"])
        st.metric("Points",payload["Total_Points"])
        st.metric("Mults",payload["Total_Mults"])
        st.metric("Current Total QSO Rate",payload["Current_Total_Rate"])
        st.metric("Top OP Score",payload["Top_OP_Score"]) 
    # Latest QSO
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
    # Radio Data
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


app()