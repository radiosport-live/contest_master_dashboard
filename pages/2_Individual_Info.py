import streamlit as st 
import geopandas as gpd
import geojson, json
import pandas as pd
import numpy as np
import dashboard_default as dash
import leafmap.foliumap as leafmap
import time
st.set_page_config(layout="wide")
@st.experimental_memo
def commands_sql():
    commands={}
    command_run="(select external_call as 'Last Run QSO', SEC_TO_TIME(timestampdiff(SECOND,`timestamp`,current_timestamp())) as Time from qsos as q where q.mycall ='"+chosen_callsign+"' and IsRunQSO=1 ORDER BY timestamp DESC LIMIT 1)"
    #st.write(dash.run_query(dash.connect(),"SELECT * from qsos limit 1;"))
    command_sp="(select external_call as 'Last Run QSO', SEC_TO_TIME(timestampdiff(SECOND,`timestamp`,current_timestamp())) as Time from qsos as q where q.mycall ='"+chosen_callsign+"' and IsRunQSO=0 ORDER BY timestamp DESC LIMIT 1);"
    commands["Ops"]="Select JSON_ONJECT(c.Top_OP_Mults, c.Top_OP_Score FROM calculated AS c WHERE c.Contest_Call="+chosen_callsign+"ORDER BY c.timestamp DESC LIMIT 1;"
    commands["radio1"]="SELECT r.OpCall, r.IsRunning, r.Freq/100 as Freq, r.FunctionKeyCaption as Macro, r.IsTransmitting, r.FocusRadioNr from radio AS r WHERE r.station_call='"+chosen_callsign+"' and r.RadioNr=1 ORDER BY r.timestamp DESC Limit 1;" 
    commands["radio2"]="SELECT r.OpCall, r.IsRunning, r.Freq/100 as Freq, r.FunctionKeyCaption as Macro, r.IsTransmitting, r.FocusRadioNr from radio AS r WHERE r.station_call='"+chosen_callsign+"' and r.RadioNr=2 ORDER BY r.timestamp DESC Limit 1;"
    commands["score"]="SELECT (s.totalpoints * s.totalmults) as 'Total Score', s.totalnoqsos as QSOs, s.totalpoints as Points, s.totalmults as Mults, s.total_rate FROM score AS s WHERE s.station_call='"+chosen_callsign+"' ORDER BY s.timestamp DESC LIMIT 1;"
    commands["q"]="SELECT q.external_call, q.band, q.mode, q.zone as exchange, q.distance, q.operator FROM qsos as q where q.`mycall`='"+chosen_callsign+"' ORDER BY q.timestamp DESC LIMIT 1;"
    commands["dash"]=command_run+" UNION "+command_sp
    return commands
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
def update_values(connection,commands):
    dash_qsos=dash.run_query(connection,commands["dash"])
    last_qso=dash.run_query(connection,commands["q"]).to_dict()
    value_radio1=dash.run_query(connection,commands["radio1"]).to_dict()
    value_radio2=dash.run_query(connection,commands["radio2"]).to_dict()
    score_update=dash.run_query(connection,commands["score"]).to_dict()
# Sidebar Configuration
# Payload Defaults
    payload={}
    payload["dashboard_qso"]=dash_qsos
    payload["last_qso"]=last_qso
    payload["score"]=score_update
    payload["radio1"]=value_radio1
    payload["radio2"]=value_radio2
    return payload
def display(chosen_callsign,time_value,payload,qsos):
    with placeholder.container():
        #payload=select_individual_data(chosen_callsign)
        col_LastQSO, col_CurrentQSO, col_Score = st.columns([.9,5,1])
        # Last QSO Info
        with col_LastQSO:
            st.markdown("## Last QSO's")
            try:
                st.metric("Last Run QSO",payload["dashboard_qso"]["Last Run QSO"][0])
                st.metric("Last Run QSO",str(payload["dashboard_qso"]["Time"][0])[-8:])
                st.metric("Last S&P QSO",payload["dashboard_qso"]["Last Run QSO"][1])
                st.metric("Last S&P QSO",str(payload["dashboard_qso"]["Time"][1])[-8:])
                st.metric("Top OP Mults",payload["Top_OP_Mults"])                  
            except (IndexError):
                st.metric("Last Run QSO","-")
                st.metric("Last Run QSO","-")
                st.metric("Last S&P QSO","-")
                st.metric("Last S&P QSO","-")
                st.metric("Top OP Mults","-")
        # QSO Map
        with col_CurrentQSO:
            st.markdown("<h2><center> QSO Map </center></h2>",unsafe_allow_html=True) 
            #st.write(qso_line_layer)
            try:
                base_map.remove_layer("QSOs")
                base_map.add_gdf(qsos, layer_name="QSOs")
            except IndexError:
                with st.sidebar:
                    st.text("No QSOs in last "+str(time_value)+" minutes.")
            except :
                with st.sidebar:
                    st.text("Error on QSO Layer")
            base_map.to_streamlit(width=900, height=550)
        # Score Column
        with col_Score:
            st.markdown("## Score")
            try:
                st.metric("Total Score",payload["score"]["Total Score"][0])
                st.metric("QSO's",payload["score"]["QSOs"][0])
                st.metric("Points",payload["score"]["Points"][0])
                st.metric("Mults",payload["score"]["Mults"][0])
                st.metric("Current Total QSO Rate",payload["score"]["total_rate"][0])
                st.metric("Top OP Score",payload["Top_OP_Score"]) 
            except (IndexError, KeyError) as error:
                st.metric("Total Score","-")
                st.metric("QSO's","-")
                st.metric("Points","-")
                st.metric("Mults","-")
                st.metric("Current Total QSO Rate","-")
    # Latest QSO
    with placeholder2.container():
        col_space_a, col_Last, col_Last_QSO,col_band,col_mode,col_exchange,col_distance,col_op, col_Score_b = st.columns([1.0,1.3,.7,.7,.7,.7,.7,.7,1.5])
        with col_Last:
            st.markdown("## Latest QSO:")
        try:
            with col_Last_QSO:
                st.metric("Last QSO",payload["last_qso"]["external_call"][0])
            with col_band:
                st.metric("Band",payload["last_qso"]["band"][0])
            with col_mode:
                st.metric("Mode",payload["last_qso"]["mode"][0])
            with col_exchange:
                st.metric("Exchange",payload["last_qso"]["exchange"][0])
            with col_distance:
                st.metric("Distance",payload["last_qso"]["distance"][0])
            with col_op:
                st.metric("OP",payload["last_qso"]["operator"][0])
            with col_Score_b:
                st.empty()
        except:
            with st.sidebar:
                st.write("Missing QSOS")
    # Radio Data
    with placeholder3.container():
        col_1_title, col_2_title= st.columns([1,1])
        with col_1_title:
            st.title("Radio 1 Data")
        with col_2_title:
            st.title("Radio 2 Data")
        col_1,col_2,col_3,col_4,col_5,col_6,col_7,col_1_2,col_2_2,col_3_2,col_4_2,col_5_2,col_6_2,col_7_2= st.columns([3,2,3,2,2,2,2,3,2,3,2,2,2,2]) 
        #Radio1
        try:
            with col_1:
                st.metric("Operator",payload["radio1"]["OpCall"][0])
            with col_2:
                st.metric("Mode",payload["radio1"]["IsRunning"][0])
            with col_3:
                st.metric("Freq",payload["radio1"]["Freq"][0])
            with col_4:
                st.metric("Status",payload["radio1"]["IsTransmitting"][0])
            with col_5:
                if (payload["radio1"]["Macro"][0]==''):
                    st.metric("Macro","-")
                else:
                    st.metric("Macro",payload["radio1"]["FunctionKeyCaption"][0])
            with col_6:
                st.metric("Radio 1 Rate",payload["radio1"]["FocusRadioNr"][0])
            with col_7:
                st.markdown("TX and Focus")
        except KeyError as e:
            with col_3:
                st.write("No Radio1 Data")
            # Radio 2
        try:
            with col_1_2:
                st.metric("Operator",payload["radio2"]["OpCall"][0])
            with col_2_2:
                st.metric("Mode",payload["radio2"]["IsRunning"][0])
            with col_3_2:
                st.metric("Freq",payload["radio2"]["Freq"][0])
            with col_4_2:
                st.metric("Status",payload["radio2"]["IsTransmitting"][0])
            with col_5_2:
                st.metric("Macro",payload["radio2"]["FunctionKeyCaption"][0])
            with col_6_2:
                st.metric("Radio 2 Rate",payload["radio2"]["FocusRadioNr"][0])
            with col_7_2:
                st.markdown("TX and Focus")
        except:
            with col_3_2:
                st.write("No Radio 2 Data")
# Inits
placeholder=st.empty()
placeholder2=st.empty()
placeholder3=st.empty()
base_map = leafmap.Map(draw_export=True)
base_layer = dash.geo_map(base_map)
base_map.add_gdf(base_layer, layer_name="ARRL Sections")
base_map.set_center(-97,38,3.5)
with open("frontend/css/streamlit.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
connection=dash.connect()
# Select Callsigns and time
callsigns = dash.run_query(dash.connect(),"SELECT DISTINCT Contest_Call FROM home ORDER BY Contest_Call ASC;")
with st.sidebar:
    chosen_callsign=st.selectbox('Choose Callsign',callsigns)
    time_value=st.slider("Map Time Max",min_value=10, max_value=60,value=30, step=1)
qso_line_layer = qso_line_map(base_map,dash.connect(),chosen_callsign,"Y",time_value) 

display(chosen_callsign,time_value,update_values(connection,commands_sql()),qso_line_layer)
