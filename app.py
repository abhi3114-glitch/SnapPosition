"""
SnapPosition - Mouse Movement Personality Visualizer
A Streamlit application for capturing and analyzing mouse movement patterns.
"""

import streamlit as st
import json
import time
from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.logger import MouseLogger
from src.processor import process_data, get_hesitation_zones
from src.visualizer import (
    create_heatmap,
    create_hesitation_map,
    create_speed_distribution,
    create_path_trace,
    create_personality_summary,
    fig_to_bytes
)

# Page configuration
st.set_page_config(
    page_title="SnapPosition",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium styling
st.markdown("""
<style>
    /* Main theme */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        color: #a0a0a0;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Card styling */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.2);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        color: #888;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
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
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Status indicator */
    .status-recording {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(239, 68, 68, 0.2);
        border: 1px solid rgba(239, 68, 68, 0.5);
        border-radius: 20px;
        padding: 0.5rem 1rem;
        color: #ef4444;
        font-weight: 600;
    }
    
    .status-idle {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(34, 197, 94, 0.2);
        border: 1px solid rgba(34, 197, 94, 0.5);
        border-radius: 20px;
        padding: 0.5rem 1rem;
        color: #22c55e;
        font-weight: 600;
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1e2f 0%, #2d2d44 100%);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #888;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'logger' not in st.session_state:
    st.session_state.logger = MouseLogger()
if 'data' not in st.session_state:
    st.session_state.data = []
if 'processed' not in st.session_state:
    st.session_state.processed = None
if 'recording' not in st.session_state:
    st.session_state.recording = False


def start_recording():
    """Start mouse event recording."""
    st.session_state.logger.clear_data()
    st.session_state.logger.start()
    st.session_state.recording = True


def stop_recording():
    """Stop mouse event recording and process data."""
    st.session_state.logger.stop()
    st.session_state.data = st.session_state.logger.get_data()
    st.session_state.processed = process_data(st.session_state.data)
    st.session_state.recording = False


def export_json():
    """Export data as JSON."""
    if not st.session_state.data:
        return None
    
    export_data = {
        "metadata": {
            "export_time": datetime.now().isoformat(),
            "total_events": len(st.session_state.data),
            "app": "SnapPosition"
        },
        "statistics": st.session_state.processed["stats"] if st.session_state.processed else {},
        "events": st.session_state.data
    }
    return json.dumps(export_data, indent=2)


# Header
st.markdown('<h1 class="main-header">🎯 SnapPosition</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Behavioral Mouse Movement Personality Visualizer</p>', unsafe_allow_html=True)

# Sidebar controls
with st.sidebar:
    st.markdown("### 🎮 Controls")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("▶️ Start", use_container_width=True, disabled=st.session_state.recording):
            start_recording()
            st.rerun()
    
    with col2:
        if st.button("⏹️ Stop", use_container_width=True, disabled=not st.session_state.recording):
            stop_recording()
            st.rerun()
    
    # Status display
    st.markdown("---")
    if st.session_state.recording:
        st.markdown('<div class="status-recording pulse">🔴 Recording...</div>', unsafe_allow_html=True)
        # Show live event count
        event_count = st.session_state.logger.event_count
        st.metric("Events Captured", f"{event_count:,}")
        
        # Auto-refresh while recording
        time.sleep(0.5)
        st.rerun()
    else:
        st.markdown('<div class="status-idle">🟢 Ready</div>', unsafe_allow_html=True)
        if st.session_state.data:
            st.metric("Events in Session", f"{len(st.session_state.data):,}")
    
    # Export section
    st.markdown("---")
    st.markdown("### 📤 Export")
    
    if st.session_state.data:
        # JSON Export
        json_data = export_json()
        st.download_button(
            label="📄 Download JSON",
            data=json_data,
            file_name=f"snapposition_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    else:
        st.info("Record a session to enable exports")
    
    # Clear data
    st.markdown("---")
    if st.button("🗑️ Clear Session", use_container_width=True):
        st.session_state.data = []
        st.session_state.processed = None
        st.session_state.logger.clear_data()
        st.rerun()


# Main content area
if st.session_state.processed and st.session_state.data:
    stats = st.session_state.processed["stats"]
    
    # Statistics cards
    st.markdown("### 📊 Session Statistics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{:,}</div>
            <div class="metric-label">Events</div>
        </div>
        """.format(stats["total_events"]), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Clicks</div>
        </div>
        """.format(stats["total_clicks"]), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{:.1f}s</div>
            <div class="metric-label">Duration</div>
        </div>
        """.format(stats["duration"]), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{:.0f}</div>
            <div class="metric-label">Avg Speed</div>
        </div>
        """.format(stats["avg_speed"]), unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{:,.0f}</div>
            <div class="metric-label">Distance (px)</div>
        </div>
        """.format(stats["distance_traveled"]), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Visualization tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔥 Heatmap", 
        "⏸️ Hesitation", 
        "⚡ Speed", 
        "🛤️ Path",
        "🎭 Personality"
    ])
    
    with tab1:
        st.markdown("### Movement Density Heatmap")
        fig = create_heatmap(st.session_state.processed)
        st.pyplot(fig)
        
        # Export button
        img_bytes = fig_to_bytes(fig)
        st.download_button(
            label="📷 Download Heatmap",
            data=img_bytes,
            file_name="heatmap.png",
            mime="image/png"
        )
    
    with tab2:
        st.markdown("### Hesitation Zones")
        st.caption("Areas where the mouse lingered or moved slowly")
        
        fig = create_hesitation_map(st.session_state.processed)
        st.pyplot(fig)
        
        # Show top hesitation zones
        zones = get_hesitation_zones(st.session_state.processed)
        if zones:
            st.markdown("#### Top Hesitation Zones")
            for i, (x, y, dwell) in enumerate(zones, 1):
                st.write(f"{i}. Grid ({x}, {y}) - Dwell time: {dwell:.2f}s")
        
        img_bytes = fig_to_bytes(fig)
        st.download_button(
            label="📷 Download Hesitation Map",
            data=img_bytes,
            file_name="hesitation_map.png",
            mime="image/png"
        )
    
    with tab3:
        st.markdown("### Speed Distribution Analysis")
        
        fig = create_speed_distribution(st.session_state.processed)
        st.pyplot(fig)
        
        # Speed stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Speed", f"{stats['avg_speed']:.1f} px/s")
        with col2:
            st.metric("Max Speed", f"{stats['max_speed']:.1f} px/s")
        with col3:
            st.metric("Speed Std Dev", f"{stats['speed_std']:.1f}")
        
        img_bytes = fig_to_bytes(fig)
        st.download_button(
            label="📷 Download Speed Chart",
            data=img_bytes,
            file_name="speed_distribution.png",
            mime="image/png"
        )
    
    with tab4:
        st.markdown("### Movement Path Trace")
        
        show_clicks = st.checkbox("Show click positions", value=True)
        fig = create_path_trace(st.session_state.processed, show_clicks=show_clicks)
        st.pyplot(fig)
        
        img_bytes = fig_to_bytes(fig)
        st.download_button(
            label="📷 Download Path Trace",
            data=img_bytes,
            file_name="path_trace.png",
            mime="image/png"
        )
    
    with tab5:
        st.markdown("### Personality Analysis Summary")
        st.caption("A comprehensive view of your mouse movement behavior")
        
        fig = create_personality_summary(st.session_state.processed)
        st.pyplot(fig)
        
        img_bytes = fig_to_bytes(fig)
        st.download_button(
            label="📷 Download Personality Summary",
            data=img_bytes,
            file_name="personality_summary.png",
            mime="image/png"
        )

else:
    # Empty state
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">🖱️</div>
        <h2 style="color: #888; margin-bottom: 1rem;">No Recording Yet</h2>
        <p style="color: #666; max-width: 400px; margin: 0 auto;">
            Click the <strong>Start</strong> button in the sidebar to begin capturing 
            your mouse movements. Move your mouse around the screen to generate data,
            then click <strong>Stop</strong> to see your analysis.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Instructions
    with st.expander("📖 How to Use"):
        st.markdown("""
        1. **Start Recording**: Click the ▶️ Start button in the sidebar
        2. **Move Your Mouse**: Navigate around your screen naturally
        3. **Click Around**: The tool tracks clicks as decision points
        4. **Stop Recording**: Click ⏹️ Stop when finished
        5. **Explore Analysis**: View your heatmap, hesitation zones, and more
        6. **Export**: Download your data as JSON or images
        
        **Privacy Note**: All data stays local. Nothing is sent to any server.
        """)
