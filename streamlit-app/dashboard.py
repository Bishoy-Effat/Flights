import streamlit as st
import pandas as pd
import psycopg2
import folium
from streamlit_folium import st_folium
import ast
from datetime import datetime
import plotly.express as px

# 🎨 Ultra-Modern Page Configuration
st.set_page_config(
    page_title="AeroVision Pro | Live Flight Intelligence", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎯 Advanced Custom CSS with Glass Morphism & Animations
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 6s infinite linear;
    }
    
    @keyframes pulse {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 1.8rem;
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.2);
    }
    
    .metric-glassy {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        backdrop-filter: blur(15px);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
        text-align: center;
        color: white;
        transition: all 0.3s ease;
    }
    
    .metric-glassy:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3));
        transform: scale(1.05);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 16px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.6);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
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
    
    /* Progress bars */
    .progress-container {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        height: 8px;
        margin: 8px 0;
        overflow: hidden;
    }
    
    .progress-bar {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #00b09b, #96c93d);
        transition: width 0.5s ease;
        position: relative;
    }
    
    .progress-bar::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
        background-image: linear-gradient(
            -45deg,
            rgba(255, 255, 255, 0.2) 25%,
            transparent 25%,
            transparent 50%,
            rgba(255, 255, 255, 0.2) 50%,
            rgba(255, 255, 255, 0.2) 75%,
            transparent 75%,
            transparent
        );
        background-size: 50px 50px;
        animation: move 2s linear infinite;
    }
    
    @keyframes move {
        0% { background-position: 0 0; }
        100% { background-position: 50px 50px; }
    }
    
    /* Status badges */
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .status-ontime { background: #00b09b; color: white; }
    .status-delayed { background: #ff9a00; color: white; }
    .status-cancelled { background: #ff4757; color: white; }
    .status-inflight { background: #5352ed; color: white; }
</style>
""", unsafe_allow_html=True)

# 🎯 Enhanced Database Connection
@st.cache_resource
def get_database_connection():
    """Create cached database connection"""
    try:
        conn = psycopg2.connect(
            dbname="flights_project",
            user="admin",
            password="admin",
            host="postgres_general"
        )
        return conn
    except Exception as e:
        st.error(f"🚨 Database connection failed: {str(e)}")
        return None

# 🎯 Smart Data Loading with Caching
@st.cache_data(ttl=60)
def load_all_flights():
    """Load ALL flights from database with smart caching"""
    try:
        conn = get_database_connection()
        if conn:
            # Enhanced query with additional potential fields
            query = """
            SELECT flight_id, origin, destination, status, departure_time, arrival_time 
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
        st.sidebar.error(f"🚨 Database error: {str(e)}")
        return pd.DataFrame()

# 🎯 Advanced Data Processing
def process_flight_data(df):
    if df.empty:
        return df
    
    try:
        # Convert coordinates from string to list
        df["origin_coord"] = df["origin"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        df["destination_coord"] = df["destination"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        
        # Convert timestamps to datetime
        df["departure_datetime"] = df["departure_time"].apply(lambda x: datetime.fromtimestamp(x))
        df["arrival_datetime"] = df["arrival_time"].apply(lambda x: datetime.fromtimestamp(x))
        df["flight_duration"] = (df["arrival_datetime"] - df["departure_datetime"]).dt.total_seconds() / 3600
        
        # Enhanced progress calculation with flight phases
        now = datetime.now()
        df["progress"] = df.apply(lambda row: min(1.0, max(0.0, 
            (now - row["departure_datetime"]).total_seconds() / 
            max(1, (row["arrival_datetime"] - row["departure_datetime"]).total_seconds()))), axis=1)
        
        # Calculate current position coordinates
        df["current_lat"] = df.apply(lambda row: 
            row["origin_coord"][0] + (row["destination_coord"][0] - row["origin_coord"][0]) * row["progress"], axis=1)
        df["current_lon"] = df.apply(lambda row: 
            row["origin_coord"][1] + (row["destination_coord"][1] - row["origin_coord"][1]) * row["progress"], axis=1)
        
        # Add flight phase detection
        def get_flight_phase(progress):
            if progress < 0.1: return "Takeoff"
            elif progress < 0.3: return "Climbing"
            elif progress < 0.7: return "Cruising"
            elif progress < 0.9: return "Descending"
            else: return "Landing"
        
        df["flight_phase"] = df["progress"].apply(get_flight_phase)
        
        # Add estimated arrival time
        df["eta"] = df.apply(lambda row: 
            row["departure_datetime"] + (row["arrival_datetime"] - row["departure_datetime"]) * row["progress"], axis=1)
        
        return df
    except Exception as e:
        st.error(f"🚨 Data processing error: {str(e)}")
        return df

# 🎯 Create Interactive Flight Map
def create_interactive_flight_map(df):
    """Create an enhanced interactive flight map"""
    
    # Create advanced base map
    m = folium.Map(
        location=[30, 0],
        zoom_start=2,
        tiles='CartoDB dark_matter',
        zoom_control=True,
        scrollWheelZoom=True
    )
    
    # Enhanced status colors
    status_colors = {
        "On Time": "#00b09b",
        "Delayed": "#ff9a00", 
        "Cancelled": "#ff4757",
        "In Flight": "#5352ed"
    }
    
    all_coordinates = []
    
    # Add each flight with enhanced visuals
    for index, flight in df.iterrows():
        color = status_colors.get(flight["status"], "#5352ed")
        current_position = [flight["current_lat"], flight["current_lon"]]
        
        # Enhanced flight path with gradient effect
        folium.PolyLine(
            locations=[flight["origin_coord"], flight["destination_coord"]],
            color=color,
            weight=3,
            opacity=0.8,
            dash_array="10, 5" if flight["status"] == "Delayed" else None,
            popup=f"Flight {flight['flight_id']} - {flight['status']}"
        ).add_to(m)
        
        # Smart aircraft marker
        folium.Marker(
            location=current_position,
            popup=folium.Popup(f"""
                <div style="width: 280px; font-family: Arial;">
                    <div style="background: linear-gradient(135deg, {color}, #2c3e50); padding: 15px; border-radius: 10px 10px 0 0; color: white;">
                        <h4 style="margin: 0;">✈️ {flight['flight_id']}</h4>
                    </div>
                    <div style="padding: 15px; background: white; border-radius: 0 0 10px 10px;">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
                            <div><strong>🛫 From:</strong><br>{flight['origin']}</div>
                            <div><strong>🛬 To:</strong><br>{flight['destination']}</div>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <div><strong>📊 Status:</strong><br><span style="color: {color}; font-weight: bold;">{flight['status']}</span></div>
                            <div><strong>🎯 Phase:</strong><br>{flight['flight_phase']}</div>
                        </div>
                        <div style="margin-top: 10px;">
                            <strong>⏱️ Progress:</strong>
                            <div style="background: #f0f0f0; border-radius: 10px; height: 8px; margin: 5px 0;">
                                <div style="background: {color}; width: {flight['progress']*100}%; height: 100%; border-radius: 10px;"></div>
                            </div>
                            <div style="text-align: center; font-size: 0.9em;">{flight['progress']:.1%}</div>
                        </div>
                    </div>
                </div>
            """, max_width=300),
            icon=folium.Icon(color=color, icon="plane", prefix="fa"),
            tooltip=f"✈️ {flight['flight_id']} • {flight['status']} • {flight['flight_phase']}"
        ).add_to(m)
        
        # Enhanced airport markers
        folium.CircleMarker(
            location=flight["origin_coord"],
            radius=6,
            popup=f"🛫 Origin: {flight['origin']}",
            color="white",
            fill=True,
            fillColor="#00b09b",
            fillOpacity=0.9,
            weight=2
        ).add_to(m)
        
        folium.CircleMarker(
            location=flight["destination_coord"],
            radius=6,
            popup=f"🛬 Destination: {flight['destination']}",
            color="white",
            fill=True,
            fillColor="#ff4757",
            fillOpacity=0.9,
            weight=2
        ).add_to(m)
        
        # Collect coordinates for map bounds
        all_coordinates.extend([flight["origin_coord"], flight["destination_coord"], current_position])
    
    # Fit map to show all flights
    if all_coordinates:
        m.fit_bounds(all_coordinates)
    
    return m

# 🎯 Create Advanced Statistics Dashboard
def create_advanced_statistics(df):
    if df.empty:
        return
        
    total = len(df)
    on_time = len(df[df["status"] == "On Time"])
    delayed = len(df[df["status"] == "Delayed"])
    cancelled = len(df[df["status"] == "Cancelled"])
    in_flight = len(df[df["status"] == "In Flight"]) if "In Flight" in df["status"].values else 0
    
    # Create glassy metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    metrics = [
        {"value": total, "label": "Total Flights", "icon": "📊", "color": "#5352ed"},
        {"value": on_time, "label": "On Time", "icon": "✅", "color": "#00b09b"},
        {"value": delayed, "label": "Delayed", "icon": "⏰", "color": "#ff9a00"},
        {"value": cancelled, "label": "Cancelled", "icon": "❌", "color": "#ff4757"},
        {"value": in_flight, "label": "In Flight", "icon": "✈️", "color": "#3742fa"}
    ]
    
    for col, metric in zip([col1, col2, col3, col4, col5], metrics):
        with col:
            percentage = f"{(metric['value']/total)*100:.1f}%" if total > 0 else "0%"
            st.markdown(f"""
            <div class="metric-glassy">
                <div style="font-size: 2rem; margin-bottom: 8px;">{metric['icon']}</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: {metric['color']};">{metric['value']}</div>
                <div style="font-size: 1rem; opacity: 0.9; margin-bottom: 5px;">{metric['label']}</div>
                <div style="font-size: 0.8rem; opacity: 0.7;">{percentage}</div>
            </div>
            """, unsafe_allow_html=True)

# 🎯 Create Enhanced Charts
def create_enhanced_charts(df):
    if df.empty:
        return
        
    col1, col2 = st.columns(2)
    
    with col1:
        # Enhanced status pie chart
        status_counts = df["status"].value_counts()
        fig_pie = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title=f"🔄 Flight Status Distribution",
            color_discrete_map={
                "On Time": "#00b09b",
                "Delayed": "#ff9a00", 
                "Cancelled": "#ff4757",
                "In Flight": "#5352ed"
            },
            hole=0.4
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(
            font=dict(size=12),
            showlegend=False,
            margin=dict(t=50, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Enhanced flights by hour with phases
        df["departure_hour"] = df["departure_datetime"].dt.hour
        df["flight_phase_color"] = df["flight_phase"].map({
            "Takeoff": "#ff6b6b",
            "Climbing": "#4ecdc4", 
            "Cruising": "#45b7d1",
            "Descending": "#96ceb4",
            "Landing": "#feca57"
        })
        
        hourly_phase_data = df.groupby(["departure_hour", "flight_phase"]).size().reset_index(name="count")
        
        fig_bar = px.bar(
            hourly_phase_data,
            x="departure_hour", 
            y="count",
            color="flight_phase",
            title="🕒 Flights by Departure Hour & Phase",
            labels={"departure_hour": "Hour of Day", "count": "Number of Flights"},
            color_discrete_map={
                "Takeoff": "#ff6b6b",
                "Climbing": "#4ecdc4", 
                "Cruising": "#45b7d1",
                "Descending": "#96ceb4",
                "Landing": "#feca57"
            }
        )
        fig_bar.update_layout(
            xaxis=dict(tickmode='linear', dtick=1),
            bargap=0.1
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# 🎯 Create Flight Phase Visualization
def create_flight_phase_analysis(df):
    """Create advanced flight phase analysis"""
    if df.empty:
        return
    
    st.markdown("### 🎯 Flight Phase Analysis")
    
    # Flight phase distribution
    phase_counts = df["flight_phase"].value_counts()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig_phase = px.bar(
            x=phase_counts.index,
            y=phase_counts.values,
            title="Current Flight Phase Distribution",
            labels={"x": "Flight Phase", "y": "Number of Flights"},
            color=phase_counts.index,
            color_discrete_sequence=['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57']
        )
        st.plotly_chart(fig_phase, use_container_width=True)
    
    with col2:
        # Phase statistics
        st.markdown("""
        <div style='background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px;'>
            <h4 style='margin-top: 0;'>📈 Phase Insights</h4>
        """, unsafe_allow_html=True)
        
        for phase, count in phase_counts.items():
            percentage = (count / len(df)) * 100
            st.metric(f"{phase}", f"{count}", f"{percentage:.1f}%")
        
        st.markdown('</div>', unsafe_allow_html=True)

# 🎯 Enhanced Main Application
def main():
    # Ultra-Modern Header
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 3rem; font-weight: 700;">🌌 AeroVision Pro</h1>
        <p style="margin: 0; font-size: 1.3rem; opacity: 0.9;">Next-Generation Flight Intelligence Platform</p>
        <div style="margin-top: 1rem;">
            <span style="background: rgba(255,255,255,0.2); padding: 8px 20px; border-radius: 25px; font-size: 1rem; font-weight: 500;">
                🚀 Live Tracking • Real-time Analytics • Predictive Insights
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if "flight_data" not in st.session_state:
        st.session_state.flight_data = None
        st.session_state.last_update = None
        st.session_state.data_loaded = False
    
    # Enhanced Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2>🎮 Control Center</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Data control in glass card
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📡 Data Management")
        
        if st.button("🔄 Sync Live Data", type="primary"):
            with st.spinner("🛰️ Syncing with satellite data..."):
                raw_data = load_all_flights()
                if not raw_data.empty:
                    processed_data = process_flight_data(raw_data)
                    st.session_state.flight_data = processed_data
                    st.session_state.last_update = datetime.now()
                    st.session_state.data_loaded = True
                    st.success("✅ Data synchronized!")
        
        if st.session_state.last_update:
            st.info(f"🕒 Last Sync: {st.session_state.last_update.strftime('%H:%M:%S')}")
            minutes_ago = int((datetime.now() - st.session_state.last_update).total_seconds() // 60)
            if minutes_ago > 0:
                st.caption(f"Updated {minutes_ago} minute{'s' if minutes_ago > 1 else ''} ago")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhanced filters in glass card
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🔍 Smart Filters")
        
        if st.session_state.flight_data is not None:
            df = st.session_state.flight_data
            
            available_statuses = df["status"].unique().tolist()
            selected_statuses = st.multiselect(
                "Flight Status:",
                available_statuses,
                default=available_statuses,
                key="status_filter"
            )
            
            available_phases = df["flight_phase"].unique().tolist()
            selected_phases = st.multiselect(
                "Flight Phase:",
                available_phases,
                default=available_phases,
                key="phase_filter"
            )
            
            # Progress filter
            progress_range = st.slider(
                "Flight Progress Range:",
                0.0, 1.0, (0.0, 1.0),
                key="progress_filter"
            )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Auto-load data on first run
    if not st.session_state.data_loaded:
        with st.spinner("🛰️ Initializing satellite connection..."):
            raw_data = load_all_flights()
            if not raw_data.empty:
                processed_data = process_flight_data(raw_data)
                st.session_state.flight_data = processed_data
                st.session_state.last_update = datetime.now()
                st.session_state.data_loaded = True
    
    # Get data
    df = st.session_state.flight_data
    
    if df is None or df.empty:
        st.error("🚨 No flight data available. Please check database connection.")
        return
    
    # Apply filters
    filtered_df = df.copy()
    if 'selected_statuses' in locals() and selected_statuses:
        filtered_df = filtered_df[filtered_df["status"].isin(selected_statuses)]
    if 'selected_phases' in locals() and selected_phases:
        filtered_df = filtered_df[filtered_df["flight_phase"].isin(selected_phases)]
    if 'progress_range' in locals():
        filtered_df = filtered_df[
            (filtered_df["progress"] >= progress_range[0]) & 
            (filtered_df["progress"] <= progress_range[1])
        ]
    
    # Show filtered count
    st.sidebar.info(f"📊 Displaying: {len(filtered_df)} / {len(df)} flights")
    
    if filtered_df.empty:
        st.warning("⚠️ No flights match your filter criteria.")
        return
    
    # Enhanced Statistics
    create_advanced_statistics(filtered_df)
    
    # Interactive Map Section
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h2>🌍 Live Flight Tracking</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    flight_map = create_interactive_flight_map(filtered_df)
    map_data = st_folium(
        flight_map, 
        width=None, 
        height=600,
        key=f"enhanced_map_{len(filtered_df)}"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Analytics Section
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h2>📊 Advanced Analytics</h2>
    </div>
    """, unsafe_allow_html=True)
    
    create_enhanced_charts(filtered_df)
    create_flight_phase_analysis(filtered_df)
    
    # Enhanced Flight Details
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h2>📋 Flight Intelligence</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    # Prepare enhanced table data
    table_data = filtered_df[[
        "flight_id", "origin", "destination", "status", "flight_phase",
        "departure_datetime", "arrival_datetime", "flight_duration", "progress", "eta"
    ]].copy()
    
    table_data["departure_datetime"] = table_data["departure_datetime"].dt.strftime("%Y-%m-%d %H:%M")
    table_data["arrival_datetime"] = table_data["arrival_datetime"].dt.strftime("%Y-%m-%d %H:%M")
    table_data["eta"] = table_data["eta"].dt.strftime("%H:%M")
    table_data["flight_duration"] = table_data["flight_duration"].apply(lambda x: f"{x:.1f}h")
    
    # Rename columns
    table_data.columns = [
        "Flight ID", "Origin", "Destination", "Status", "Phase",
        "Departure", "Arrival", "Duration", "Progress", "ETA"
    ]
    
    # Display enhanced table
    st.dataframe(
        table_data,
        use_container_width=True,
        height=400
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Modern Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>🌌 <strong>AeroVision Pro</strong> - Next Generation Aviation Intelligence • Built with Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()