import streamlit as st
import pandas as pd
import psycopg2
import folium
from streamlit_folium import st_folium
import ast
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from streamlit_autorefresh import st_autorefresh

# 🎨 Modern Page Configuration
st.set_page_config(
    page_title="SkyVision 360° | Live Flight Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🎯 Advanced Custom CSS with Glass Morphism
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 100" fill="%23ffffff" opacity="0.1"><polygon points="0,0 1000,50 1000,100 0,100"/></svg>');
        background-size: cover;
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #2c3e50, #34495e);
        border-radius: 16px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.1);
        border-radius: 12px 12px 0 0;
        padding: 12px 24px;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Progress bars */
    .progress-container {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        height: 8px;
        margin: 10px 0;
    }
    
    .progress-bar {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #00b09b, #96c93d);
        transition: width 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# 🎯 Enhanced Database Connection with Connection Pooling
@st.cache_resource(ttl=300)
def get_database_connection():
    """Create database connection with caching"""
    try:
        conn = psycopg2.connect(
            dbname="flights_project",
            user="admin",
            password="admin",
            host="postgres_general",
            connect_timeout=10
        )
        return conn
    except Exception as e:
        st.error(f"🚨 Database connection failed: {str(e)}")
        return None

# 🎯 Load ALL flights from database with advanced caching
@st.cache_data(ttl=60, show_spinner="🔄 Loading real-time flight data...")
def load_all_flights():
    """Load ALL flights from database with enhanced error handling"""
    try:
        conn = get_database_connection()
        if conn:
            # Enhanced query with additional fields
            query = """
            SELECT 
                flight_id, 
                origin, 
                destination, 
                status, 
                departure_time, 
                arrival_time,
                airline,
                aircraft_type,
                speed,
                altitude
            FROM flights 
            ORDER BY departure_time DESC
            """
            df = pd.read_sql(query, conn)
            conn.close()
            
            if not df.empty:
                st.sidebar.success(f"🎯 Loaded {len(df)} flights")
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"🚨 Database error: {str(e)}")
        return pd.DataFrame()

# 🎯 Advanced Data Processing
def process_flight_data(df):
    if df.empty:
        return df
    
    try:
        # Convert coordinates
        df["origin_coord"] = df["origin"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        df["destination_coord"] = df["destination"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        
        # Enhanced timestamp processing
        df["departure_datetime"] = pd.to_datetime(df["departure_time"], unit='s')
        df["arrival_datetime"] = pd.to_datetime(df["arrival_time"], unit='s')
        
        # Calculate advanced metrics
        df["flight_duration"] = (df["arrival_datetime"] - df["departure_datetime"]).dt.total_seconds() / 3600
        
        # Real-time progress calculation
        now = datetime.now()
        df["progress"] = df.apply(lambda row: min(1.0, max(0.0, 
            (now - row["departure_datetime"]).total_seconds() / 
            max(1, (row["arrival_datetime"] - row["departure_datetime"]).total_seconds()))), axis=1)
        
        # 3D flight path interpolation
        df["current_lat"] = df.apply(lambda row: 
            row["origin_coord"][0] + (row["destination_coord"][0] - row["origin_coord"][0]) * row["progress"], axis=1)
        df["current_lon"] = df.apply(lambda row: 
            row["origin_coord"][1] + (row["destination_coord"][1] - row["origin_coord"][1]) * row["progress"], axis=1)
        
        # Estimated time of arrival
        df["eta"] = df.apply(lambda row: 
            row["departure_datetime"] + (row["arrival_datetime"] - row["departure_datetime"]) * row["progress"], axis=1)
        
        # Flight phase detection
        def get_flight_phase(progress):
            if progress < 0.1: return "Takeoff"
            elif progress < 0.3: return "Climbing"
            elif progress < 0.7: return "Cruising"
            elif progress < 0.9: return "Descending"
            else: return "Landing"
        
        df["flight_phase"] = df["progress"].apply(get_flight_phase)
        
        return df
    except Exception as e:
        st.error(f"🚨 Data processing error: {str(e)}")
        return df

# 🎯 Create 3D Interactive Globe
def create_3d_globe(df):
    """Create an interactive 3D globe visualization"""
    fig = go.Figure()
    
    # Add flight paths
    for _, flight in df.iterrows():
        fig.add_trace(go.Scatter3d(
            x=[flight["origin_coord"][1], flight["destination_coord"][1]],
            y=[flight["origin_coord"][0], flight["destination_coord"][0]],
            z=[10000, 10000],  # Altitude
            mode='lines',
            line=dict(
                color='rgba(102, 126, 234, 0.6)',
                width=3
            ),
            name=f"Flight {flight['flight_id']}",
            showlegend=False
        ))
        
        # Add current position
        fig.add_trace(go.Scatter3d(
            x=[flight["current_lon"]],
            y=[flight["current_lat"]],
            z=[35000],  # Cruising altitude
            mode='markers',
            marker=dict(
                size=6,
                color='#ff6b6b',
                symbol='diamond'
            ),
            name=f"Position {flight['flight_id']}",
            showlegend=False
        ))
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=400
    )
    
    return fig

# 🎯 Create Advanced Flight Map
def create_advanced_flight_map(df):
    """Create an advanced interactive flight map"""
    
    # Create dark theme base map
    m = folium.Map(
        location=[30, 0],
        zoom_start=2,
        tiles='CartoDB dark_matter',
        zoom_control=True,
        scrollWheelZoom=True
    )
    
    # Enhanced status colors with gradients
    status_colors = {
        "On Time": "#00b09b",
        "Delayed": "#ff9a00",
        "Cancelled": "#ff4757",
        "In Flight": "#5352ed",
        "Boarding": "#3742fa",
        "Landed": "#2ed573"
    }
    
    # Add flight heatmap layer
    from folium.plugins import HeatMap
    heat_data = [[row["current_lat"], row["current_lon"]] for _, row in df.iterrows()]
    if heat_data:
        HeatMap(heat_data, radius=15, blur=10, gradient={
            .4: 'blue',
            .6: 'cyan',
            .7: 'lime',
            .8: 'yellow',
            .9: 'red'
        }).add_to(m)
    
    # Add each flight with enhanced visuals
    for _, flight in df.iterrows():
        color = status_colors.get(flight["status"], "#5352ed")
        
        # Animated flight path
        folium.PolyLine(
            locations=[flight["origin_coord"], flight["destination_coord"]],
            color=color,
            weight=3,
            opacity=0.8,
            dash_array="10, 5" if flight["status"] == "Delayed" else None,
            popup=f"Flight {flight['flight_id']}"
        ).add_to(m)
        
        # Smart aircraft marker with rotation
        folium.Marker(
            location=[flight["current_lat"], flight["current_lon"]],
            popup=folium.Popup(f"""
                <div style="width: 280px; font-family: Arial; color: #2c3e50;">
                    <div style="background: linear-gradient(135deg, {color}, #2c3e50); padding: 15px; border-radius: 10px; color: white;">
                        <h3 style="margin: 0;">✈️ {flight['flight_id']}</h3>
                    </div>
                    <div style="padding: 15px;">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <div><strong>🛫 Origin:</strong><br>{flight['origin']}</div>
                            <div><strong>🛬 Destination:</strong><br>{flight['destination']}</div>
                            <div><strong>📊 Status:</strong><br><span style="color: {color};">{flight['status']}</span></div>
                            <div><strong>🎯 Phase:</strong><br>{flight.get('flight_phase', 'N/A')}</div>
                            <div><strong>⏱️ Progress:</strong><br>{flight['progress']:.1%}</div>
                            <div><strong>🕒 ETA:</strong><br>{flight.get('eta', 'N/A').strftime('%H:%M')}</div>
                        </div>
                    </div>
                </div>
            """, max_width=300),
            icon=folium.DivIcon(html=f"""
                <div style="background: {color}; 
                           width: 20px; 
                           height: 20px; 
                           border-radius: 50%; 
                           border: 3px solid white;
                           box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                           transform: rotate(45deg);">
                </div>
            """)
        ).add_to(m)
    
    return m

# 🎯 Create Real-time Metrics Dashboard
def create_advanced_metrics(df):
    """Create an advanced metrics dashboard"""
    
    if df.empty:
        return
    
    total = len(df)
    metrics_data = {
        "total": total,
        "on_time": len(df[df["status"] == "On Time"]),
        "delayed": len(df[df["status"] == "Delayed"]),
        "cancelled": len(df[df["status"] == "Cancelled"]),
        "in_flight": len(df[df["status"] == "In Flight"]),
        "avg_duration": df["flight_duration"].mean(),
        "max_altitude": df.get("altitude", pd.Series([35000] * len(df))).max()
    }
    
    # Create metrics columns
    cols = st.columns(4)
    
    metrics_config = [
        {"icon": "✈️", "title": "Active Flights", "value": metrics_data["in_flight"], "suffix": "", "color": "#5352ed"},
        {"icon": "⏱️", "title": "On Time Rate", "value": f"{(metrics_data['on_time']/total)*100:.1f}", "suffix": "%", "color": "#00b09b"},
        {"icon": "🕒", "title": "Avg Duration", "value": f"{metrics_data['avg_duration']:.1f}", "suffix": "h", "color": "#ff9a00"},
        {"icon": "📊", "title": "Total Tracked", "value": total, "suffix": "", "color": "#3742fa"}
    ]
    
    for col, metric in zip(cols, metrics_config):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem; margin-bottom: 10px;">{metric['icon']}</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: {metric['color']};">
                    {metric['value']}{metric['suffix']}
                </div>
                <div style="font-size: 0.9rem; opacity: 0.8;">{metric['title']}</div>
            </div>
            """, unsafe_allow_html=True)

# 🎯 Create Predictive Analytics
def create_predictive_analytics(df):
    """Create predictive analytics and trend analysis"""
    
    if df.empty:
        return
    
    # Time-based analysis
    df["hour"] = df["departure_datetime"].dt.hour
    
    # Create analytics tabs
    tab1, tab2, tab3 = st.tabs(["📈 Trends", "🌍 Geo Analysis", "🔮 Predictions"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Flight distribution by hour
            hourly_counts = df["hour"].value_counts().sort_index()
            fig_hourly = px.area(
                x=hourly_counts.index,
                y=hourly_counts.values,
                title="Flight Distribution by Hour",
                labels={"x": "Hour of Day", "y": "Number of Flights"},
                color_discrete_sequence=["#667eea"]
            )
            st.plotly_chart(fig_hourly, use_container_width=True)
        
        with col2:
            # Status trend over time
            status_over_time = df.groupby([df["departure_datetime"].dt.date, "status"]).size().unstack(fill_value=0)
            fig_status = px.line(
                status_over_time,
                title="Flight Status Trends",
                color_discrete_map={
                    "On Time": "#00b09b",
                    "Delayed": "#ff9a00",
                    "Cancelled": "#ff4757"
                }
            )
            st.plotly_chart(fig_status, use_container_width=True)
    
    with tab2:
        # Geographic heatmap
        st.subheader("Flight Density Heatmap")
        # Add geographic analysis here
    
    with tab3:
        # Predictive insights
        st.subheader("Predictive Insights")
        
        # Calculate delay probability
        delay_prob = (len(df[df["status"] == "Delayed"]) / len(df)) * 100
        on_time_prob = 100 - delay_prob
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📊 On-time Probability", f"{on_time_prob:.1f}%")
        with col2:
            st.metric("⚠️ Delay Risk", f"{delay_prob:.1f}%")

# 🎯 Enhanced Main Application
def main():
    # Modern Header with Animation
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 3rem; font-weight: 700;">🌌 SkyVision 360°</h1>
        <p style="margin: 0; font-size: 1.2rem; opacity: 0.9;">Next-Generation Flight Intelligence Platform</p>
        <div style="margin-top: 1rem;">
            <span style="background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; font-size: 0.9rem;">
                🚀 Live • Real-time • Predictive
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Auto-refresh every 30 seconds
    st_autorefresh(interval=30000, key="data_refresh")
    
    # Initialize session state
    if "flight_data" not in st.session_state:
        st.session_state.flight_data = None
        st.session_state.last_update = None
    
    # Enhanced Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2>🎮 Control Center</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Data control section
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📡 Data Management")
        
        if st.button("🔄 Sync Live Data", type="primary", use_container_width=True):
            with st.spinner("🛰️ Syncing with satellite data..."):
                raw_data = load_all_flights()
                if not raw_data.empty:
                    processed_data = process_flight_data(raw_data)
                    st.session_state.flight_data = processed_data
                    st.session_state.last_update = datetime.now()
                    st.success("✅ Data synchronized!")
        
        if st.session_state.last_update:
            st.info(f"🕒 Last Sync: {st.session_state.last_update.strftime('%H:%M:%S')}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhanced filters
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🔍 Smart Filters")
        
        if st.session_state.flight_data is not None:
            df = st.session_state.flight_data
            
            # Multi-dimensional filtering
            status_filter = st.multiselect(
                "Flight Status",
                options=df["status"].unique(),
                default=df["status"].unique()
            )
            
            phase_filter = st.multiselect(
                "Flight Phase",
                options=df["flight_phase"].unique(),
                default=df["flight_phase"].unique()
            )
            
            # Progress slider
            progress_range = st.slider(
                "Flight Progress",
                0.0, 1.0, (0.0, 1.0),
                help="Filter flights by their journey progress"
            )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Load initial data
    if st.session_state.flight_data is None:
        with st.spinner("🛰️ Initializing satellite connection..."):
            raw_data = load_all_flights()
            if not raw_data.empty:
                processed_data = process_flight_data(raw_data)
                st.session_state.flight_data = processed_data
                st.session_state.last_update = datetime.now()
    
    df = st.session_state.flight_data
    
    if df is None or df.empty:
        st.error("🚨 No flight data available. Please check database connection.")
        return
    
    # Apply filters
    if 'status_filter' in locals() and status_filter:
        df = df[df["status"].isin(status_filter)]
    if 'phase_filter' in locals() and phase_filter:
        df = df[df["flight_phase"].isin(phase_filter)]
    if 'progress_range' in locals():
        df = df[(df["progress"] >= progress_range[0]) & (df["progress"] <= progress_range[1])]
    
    # Main Dashboard
    create_advanced_metrics(df)
    
    # Interactive Visualization Section
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h2>🌍 Live Flight Intelligence</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Map and 3D Visualization Tabs
    tab1, tab2, tab3 = st.tabs(["🗺️ Live Map", "🌐 3D Globe", "📊 Analytics"])
    
    with tab1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Real-time Flight Tracking")
        flight_map = create_advanced_flight_map(df)
        st_folium(flight_map, width=None, height=600)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("3D Flight Globe")
        globe_fig = create_3d_globe(df)
        st.plotly_chart(globe_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        create_predictive_analytics(df)
    
    # Flight Details Table with Enhanced UI
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h2>📋 Flight Details</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    # Enhanced data table
    display_columns = {
        "flight_id": "Flight ID",
        "origin": "Origin",
        "destination": "Destination", 
        "status": "Status",
        "flight_phase": "Phase",
        "progress": "Progress",
        "eta": "Estimated Arrival"
    }
    
    display_df = df[list(display_columns.keys())].copy()
    display_df.columns = display_columns.values()
    display_df["Progress"] = display_df["Progress"].apply(lambda x: f"{x:.1%}")
    display_df["Estimated Arrival"] = display_df["Estimated Arrival"].dt.strftime("%H:%M")
    
    # Add progress bars
    def style_progress_bar(val):
        progress = float(val.strip('%')) / 100
        color = "#00b09b" if progress > 0.7 else "#ff9a00" if progress > 0.3 else "#ff4757"
        return f"""
        <div class="progress-container">
            <div class="progress-bar" style="width: {progress*100}%; background: {color};"></div>
        </div>
        {val}
        """
    
    styled_df = display_df.style.format({
        'Progress': style_progress_bar
    })
    
    st.dataframe(styled_df, use_container_width=True, height=400)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>🌌 <strong>SkyVision 360°</strong> - Next Generation Aviation Intelligence • Built with Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()