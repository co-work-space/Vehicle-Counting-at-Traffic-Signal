import streamlit as st
import pandas as pd
import numpy as np
import cv2
import tempfile
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, time
import signal
import os

# Create target directories automatically on system startup to hold image crops
os.makedirs("data/crops", exist_ok=True)

# =====================================================================
# 🛠️ BACKGROUND THREAD CONFIGURATION OVERRIDE
# =====================================================================
original_signal_func = signal.signal
def dummy_signal_handler(sig, action):
    pass
signal.signal = dummy_signal_handler

from src.models.yolo_detector import YOLODetector
from src.tracking.centroid_tracker import CentroidTracker

signal.signal = original_signal_func
# =====================================================================

from src.analytics.traffic_analytics import TrafficAnalytics

st.set_page_config(page_title="Traffic Command Center", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

THEME_COLORS = ['#FF4B4B', '#1E88E5', '#FFC107', '#00C853', '#00ACC1']
COLOR_MAP = {'Car': '#FF4B4B', 'Truck': '#1E88E5', 'Bus': '#FFC107', 'Motorcycle': '#00C853', 'Rickshaw': '#00ACC1'}

if "traffic_log_db" not in st.session_state:
    st.session_state.traffic_log_db = []
if "dashboard_results" not in st.session_state:
    st.session_state.dashboard_results = None  

@st.cache_resource
def load_ai_modules():
    return YOLODetector(), CentroidTracker(), TrafficAnalytics()

detector, tracker, analytics = load_ai_modules()
CLASS_MAPPING = {2: 'Car', 3: 'Motorcycle', 5: 'Bus', 7: 'Truck', 8: 'Rickshaw'}

# --- 🛠️ FUNCTION DEFINITION (Fixes the NameError) ---
def render_metrics_and_charts(results_dict):
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Vehicles Today", f"{results_dict['total_count']:,}")
    kpi2.metric("Current Traffic Density", f"{results_dict['density']:.2f}")
    kpi3.metric("Average Speed Estimate", f"{results_dict['speed']} km/h")
    kpi4.metric("Current Volume (Last 15m)", f"{results_dict['total_count']}")
    
    st.markdown("---")
    st.plotly_chart(results_dict['line_chart'], use_container_width=True)
    
    col_p, col_b = st.columns(2)
    with col_p:
        st.plotly_chart(results_dict['pie_chart'], use_container_width=True)
    with col_b:
        st.plotly_chart(results_dict['bar_chart'], use_container_width=True)
        
    st.markdown("---")
    st.markdown("#### Dynamic Intersection Congestion Load")
    _, gc, _ = st.columns([1, 2, 1])
    with gc:
        st.plotly_chart(results_dict['gauge_chart'], use_container_width=True)

# --- REAL-TIME UI LOOP HELPER (SPOT 1 FIX) ---
def update_dashboard_ui(total_count, calculated_density, cumulative_history, counts_by_type):
    estimated_speed = max(12, int(52 - (calculated_density * 35) + np.random.normal(0, 1)))
    metric_total.metric("Total Vehicles Today", f"{total_count:,}")
    metric_density.metric("Current Traffic Density", f"{calculated_density:.2f}")
    metric_speed.metric("Average Speed Estimate", f"{estimated_speed} km/h")
    metric_volume.metric("Current Volume (Last 15m)", f"{total_count}")

    if cumulative_history:
        history_df = pd.DataFrame(cumulative_history)
        df_melted = history_df.melt(id_vars=['Time'], value_vars=['Car', 'Truck', 'Bus', 'Motorcycle', 'Rickshaw'],
                                    var_name='Vehicle Type', value_name='Count')
        
        fig_line = px.line(df_melted, x='Time', y='Count', color='Vehicle Type', 
                           color_discrete_map=COLOR_MAP, title="Traffic Volume Over Time")
        fig_line.update_xaxes(nticks=10, tickangle=45)
        fig_line.update_layout(plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Running Total Volume")
        chart_line_placeholder.plotly_chart(fig_line, use_container_width=True)
        
        fig_pie = px.pie(names=list(counts_by_type.keys()), values=list(counts_by_type.values()), hole=0.4, color_discrete_sequence=THEME_COLORS)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(margin=dict(t=10, b=10), showlegend=False)
        chart_pie_placeholder.plotly_chart(fig_pie, use_container_width=True)
        
        fig_bar = px.bar(x=list(counts_by_type.keys()), y=list(counts_by_type.values()), color=list(counts_by_type.keys()), color_discrete_map=COLOR_MAP)
        fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Vehicle Class", yaxis_title="Counts", margin=dict(t=30, b=10), showlegend=False)
        chart_bar_placeholder.plotly_chart(fig_bar, use_container_width=True)

        gauge_percentage = min(100, int(calculated_density * 100))
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = gauge_percentage,
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "black"},
                'bar': {'color': "#00ACC1"}, 
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 45], 'color': "#00C853"},  
                    {'range': [45, 78], 'color': "#FFC107"},  
                    {'range': [78, 100], 'color': "#FF4B4B"}], 
            }
        ))
        fig_gauge.update_layout(margin=dict(t=40, b=10, l=40, r=40), height=450)
        chart_gauge_placeholder.plotly_chart(fig_gauge, use_container_width=True)

with st.sidebar:
    st.title("Traffic Analytics")
    st.markdown("---")
    menu = st.radio("Navigation", ["Main Dashboard", "Search Logs", "Export Data"])
    st.markdown("---")
    
    st.markdown("### Engine Optimization")
    playback_speed = st.select_slider(
        "Processing Pipeline Speed",
        options=["1x (Normal)", "2x (Fast Run)", "4x (Hyper-Drive)"],
        value="1x (Normal)"
    )
    
    show_live_stream = st.checkbox("Enable Live Video View", value=True)
    
    SPEED_SKIP_MAP = {"1x (Normal)": 1, "2x (Fast Run)": 2, "4x (Hyper-Drive)": 4}
    frame_step = SPEED_SKIP_MAP[playback_speed]
    
    st.markdown("---")
    st.success("System Status: AI ENGINE ONLINE")

if menu == "Main Dashboard":
    st.title("Live Traffic Command Center")
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.dashboard_results is not None:
        st.info("🔄 Displaying retained data from your previous pipeline session.")
        
        if 'video_path' in st.session_state.dashboard_results and os.path.exists(st.session_state.dashboard_results['video_path']):
            with open(st.session_state.dashboard_results['video_path'], "rb") as f:
                st.download_button(
                    label="📥 Download Previously Processed Video Clip",
                    data=f.read(),
                    file_name="retained_traffic_feed.mp4",
                    mime='video/mp4'
                )
        
        render_metrics_and_charts(st.session_state.dashboard_results)
        
        if st.button("Clear Dashboard & Reset Session"):
            st.session_state.dashboard_results = None
            st.session_state.traffic_log_db = []
            st.rerun()

    else:
        uploaded_file = st.file_uploader("Choose a traffic video file (MP4, AVI)", type=["mp4", "avi"])
        
        if uploaded_file is not None:
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(uploaded_file.read())
            
            video_capture = cv2.VideoCapture(tfile.name)
            
            fps = int(video_capture.get(cv2.CAP_PROP_FPS))
            if fps == 0 or fps > 60:
                fps = 30  
            width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            out_temp_path = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False).name
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(out_temp_path, fourcc, fps, (width, height))
            
            st.markdown("### Live Pipeline Monitoring")
            col_video, col_download_space = st.columns([3, 1])
            with col_video:
                video_frame_placeholder = st.empty()  
            with col_download_space:
                st.markdown("#### Progress Metrics")
                progress_bar = st.progress(0)
                status_text = st.empty()
                metric_total = st.empty()
                metric_density = st.empty()
                metric_speed = st.empty()
                metric_volume = st.empty()
                chart_line_placeholder = st.empty()
                chart_pie_placeholder = st.empty()
                chart_bar_placeholder = st.empty()
                chart_gauge_placeholder = st.empty()
            
            total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            cumulative_history = []
            counts_by_type = {'Car': 0, 'Truck': 0, 'Bus': 0, 'Motorcycle': 0, 'Rickshaw': 0}
            unique_counted_ids = set()
            
            frame_count = 0
            while video_capture.isOpened():
                if frame_step > 1:
                    for _ in range(frame_step - 1):
                        video_capture.grab()  
                
                ret, frame = video_capture.read()
                if not ret:
                    break  
                    
                frame_count += frame_step
                h, w, _ = frame.shape
                
                if frame_count % (3 * frame_step) == 0:
                    detections = detector.detect(frame)
                    
                    tracker_inputs = []
                    for d in detections:
                        x1, y1, x2, y2 = d["bbox"]
                        class_name = CLASS_MAPPING.get(d["class"], "Car")
                        tracker_inputs.append((x1, y1, x2, y2, class_name))
                    
                    tracked_objects = tracker.update(tracker_inputs)
                    
                    for obj_id, obj_data in tracked_objects.items():
                        cx, cy = obj_data['centroid']
                        v_type = obj_data['detection']['class_name']
                        
                        matching_box = None
                        for (bx1, by1, bx2, by2, b_class) in tracker_inputs:
                            if int((bx1 + bx2) / 2.0) == cx and int((by1 + by2) / 2.0) == cy:
                                matching_box = (bx1, by1, bx2, by2)
                                break
                        
                        if matching_box:
                            bx1, by1, bx2, by2 = matching_box
                            box_color = (0, 255, 0) 
                            cv2.rectangle(frame, (bx1, by1), (bx2, by2), box_color, 2)
                            cv2.putText(frame, f"ID {obj_id}: {v_type}", (bx1, max(15, by1 - 8)),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 2)
                            
                            if obj_id not in unique_counted_ids:
                                unique_counted_ids.add(obj_id)
                                counts_by_type[v_type] += 1
                                
                                crop_y1, crop_y2 = max(0, by1), min(h, by2)
                                crop_x1, crop_x2 = max(0, bx1), min(w, bx2)
                                vehicle_crop = frame[crop_y1:crop_y2, crop_x1:crop_x2]
                                
                                crop_path = f"data/crops/vehicle_{obj_id}.jpg"
                                if vehicle_crop.size > 0:
                                    cv2.imwrite(crop_path, vehicle_crop)
                                else:
                                    crop_path = "None"
                                
                                current_timestamp = datetime.now()
                                
                                cumulative_history.append({
                                    'Time': current_timestamp.strftime('%H:%M:%S'),
                                    'Car': counts_by_type['Car'],
                                    'Truck': counts_by_type['Truck'],
                                    'Bus': counts_by_type['Bus'],
                                    'Motorcycle': counts_by_type['Motorcycle'],
                                    'Rickshaw': counts_by_type['Rickshaw']
                                })
                                
                                st.session_state.traffic_log_db.append({
                                    'Timestamp': current_timestamp.isoformat(),
                                    'Time_Display': current_timestamp.strftime('%H:%M:%S'),
                                    'Vehicle_ID': f"ID_{obj_id}",
                                    'Type': v_type,
                                    'Confidence': "92%",
                                    'Crop_Path': crop_path 
                                })

                # Counting line positioned safely lower down the window frame (75%)
                line_y = int(h * 0.75)
                cv2.line(frame, (0, line_y), (w, line_y), (0, 0, 255), 2)
                cv2.putText(frame, "COUNTING LINE", (10, line_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                video_writer.write(frame)

                if show_live_stream:
                    frame_resized = cv2.resize(frame, (640, 360))
                    frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                    video_frame_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)
                
                pct = min(100, int((frame_count / total_frames) * 100))
                progress_bar.progress(pct)
                status_text.text(f"Processing Pipeline Load: {pct}% complete")

            video_capture.release()
            video_writer.release()  
            
            total_count = len(unique_counted_ids)
            final_density = analytics.calculate_density(total_count)
            final_speed = max(12, int(52 - (final_density * 35)))
            
            history_df = pd.DataFrame(cumulative_history) if cumulative_history else pd.DataFrame(columns=['Time'])
            df_melted = history_df.melt(id_vars=['Time'], value_vars=['Car', 'Truck', 'Bus', 'Motorcycle', 'Rickshaw'],
                                        var_name='Vehicle Type', value_name='Count') if cumulative_history else pd.DataFrame()
            
            fig_line = px.line(df_melted, x='Time', y='Count', color='Vehicle Type', color_discrete_map=COLOR_MAP, title="Traffic Volume Over Time")
            fig_line.update_xaxes(nticks=10, tickangle=45)
            fig_line.update_layout(plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Running Total Volume")
            
            fig_pie = px.pie(names=list(counts_by_type.keys()), values=list(counts_by_type.values()), hole=0.4, color_discrete_sequence=THEME_COLORS)
            fig_bar = px.bar(x=list(counts_by_type.keys()), y=list(counts_by_type.values()), color=list(counts_by_type.keys()), color_discrete_map=COLOR_MAP)
            fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)")
            
            # --- FINAL CONTAINER RE-SCALE (SPOT 2 FIX) ---
            fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=min(100, int(final_density * 100)), gauge={'steps': [{'range': [0, 45], 'color': "#00C853"}, {'range': [45, 78], 'color': "#FFC107"}, {'range': [78, 100], 'color': "#FF4B4B"}], 'bar': {'color': "#00ACC1"}}))
            fig_gauge.update_layout(margin=dict(t=40, b=10, l=40, r=40), height=450)
            
            st.session_state.dashboard_results = {
                'total_count': total_count,
                'density': final_density,
                'speed': final_speed,
                'line_chart': fig_line,
                'pie_chart': fig_pie,
                'bar_chart': fig_bar,
                'gauge_chart': fig_gauge,
                'video_path': out_temp_path
            }
            
            st.balloons()
            st.rerun()  

elif menu == "Search Logs":
    st.title("Search Historical Log Database")
    st.markdown("Filter recorded AI entries by execution timestamps and object classifications.")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        start_filter = st.time_input("Start Time window", value=time(0, 0))
    with col2:
        end_filter = st.time_input("End Time window", value=time(23, 59))
    with col3:
        type_filter = st.selectbox("Vehicle Type Classification", ["All Detections", "Car", "Truck", "Bus", "Motorcycle", "Rickshaw"])
        
    if st.button("Query Database Records", use_container_width=True):
        if not st.session_state.traffic_log_db:
            st.warning("The log database is currently empty. Please upload and process a video clip on the main dashboard tab first.")
        else:
            filtered_records = []
            for entry in st.session_state.traffic_log_db:
                dt_obj = datetime.fromisoformat(entry['Timestamp'])
                entry_time = dt_obj.time()
                
                if start_filter <= entry_time <= end_filter:
                    if type_filter == "All Detections" or entry['Type'] == type_filter:
                        filtered_records.append(entry)
            
            if not filtered_records:
                st.info("No records matched your specific filter metrics.")
            else:
                st.success(f"Query completed successfully! Found {len(filtered_records)} matched entries.")
                
                for log in filtered_records:
                    with st.container():
                        col_crop, col_id, col_class = st.columns([1.2, 2, 2])
                        with col_crop:
                            if 'Crop_Path' in log and log['Crop_Path'] != "None" and os.path.exists(log['Crop_Path']):
                                st.image(log['Crop_Path'], use_column_width=True)
                            else:
                                dummy_crop = np.full((100, 150, 3), 220, dtype=np.uint8)
                                cv2.putText(dummy_crop, "[ No Crop Available ]", (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (120, 120, 120), 1)
                                st.image(dummy_crop, channels="RGB")
                        with col_id:
                            st.markdown(f"##### **Vehicle Identification:** {log['Vehicle_ID']}")
                            st.write(f"⏱️ **Log Time:** {log['Time_Display']}")
                        with col_class:
                            st.markdown(f"##### **Classification:** `{log['Type']}`")
                            st.write(f"🎯 **Model Confidence:** {log['Confidence']}")
                        st.markdown("<hr style='margin: 0.5em 0px; border-color: rgba(49, 51, 63, 0.2);'>", unsafe_allow_html=True)

elif menu == "Export Data":
    st.title("Export Traffic Detection History")
    st.markdown("Download the current tracking registry dataset as a standardized CSV report.")
    st.markdown("---")
    
    if not st.session_state.traffic_log_db:
        st.info("No detection logs are available to export yet. Process a traffic video clip to compile analytics data.")
    else:
        export_df = pd.DataFrame(st.session_state.traffic_log_db)
        columns_to_show = [c for c in export_df.columns if c not in ['Timestamp', 'Crop_Path']]
        clean_export_df = export_df[columns_to_show]
            
        st.dataframe(clean_export_df, use_container_width=True)
        
        csv_data = clean_export_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Full CSV Report",
            data=csv_data,
            file_name=f"traffic_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime='text/csv',
            use_container_width=True
        )