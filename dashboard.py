import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import numpy as np
from pathlib import Path

# Set page configuration for mobile responsiveness
st.set_page_config(
    page_title="India Crime Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for mobile responsiveness
st.markdown("""
    <style>
    /* Base styles */
    .main {
        padding: 0.5rem;
    }
    
    /* Mobile-specific styles */
    @media (max-width: 768px) {
        .main {
            padding: 0.25rem;
        }
        
        /* Make sidebar more compact on mobile */
        .sidebar .sidebar-content {
            padding: 0.5rem;
        }
        
        /* Improve touch targets */
        .stButton>button {
            width: 100%;
            padding: 1rem;
            font-size: 1.1rem;
        }
        
        .stSelectbox, .stSlider {
            width: 100%;
            padding: 0.75rem 0;
            font-size: 1.1rem;
        }
        
        /* Optimize chart containers */
        .element-container {
            margin: 0.5rem 0;
            width: 100%;
        }
        
        /* Make tabs more touch-friendly */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            flex-wrap: wrap;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.75rem 1.25rem;
            font-size: 1rem;
            min-width: 120px;
        }
        
        /* Improve map responsiveness */
        .folium-map {
            height: 600px !important;
            width: 100% !important;
        }
        
        /* Make headers more readable */
        h1 {
            font-size: 1.75rem;
        }
        
        h2 {
            font-size: 1.4rem;
        }
        
        h3 {
            font-size: 1.2rem;
        }
        
        /* Improve chart readability */
        .stPlotlyChart {
            width: 100% !important;
            height: 600px !important;
        }
        
        /* Make data tables more mobile-friendly */
        .stDataFrame {
            width: 100%;
            overflow-x: auto;
            font-size: 0.9rem;
        }
    }
    
    /* Desktop-specific styles */
    @media (min-width: 769px) {
        .main {
            padding: 1rem;
        }
        
        .sidebar .sidebar-content {
            padding: 1rem;
        }
        
        .stPlotlyChart {
            height: 600px !important;
        }
    }
    
    /* Common styles */
    .stDataFrame {
        width: 100%;
        overflow-x: auto;
    }
    
    /* Improve filter section visibility */
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
        border-radius: 0.5rem;
    }
    
    /* Add some spacing between elements */
    .element-container {
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Function to load and preprocess data
@st.cache_data
def load_data():
    # Load IPC crimes data
    ipc_2013 = pd.read_csv('Datasets/01_District_wise_crimes_committed_IPC_2013.csv')
    ipc_2001_2012 = pd.read_csv('Datasets/01_District_wise_crimes_committed_IPC_2001_2012.csv')
    
    # Combine datasets
    ipc_data = pd.concat([ipc_2001_2012, ipc_2013])
    
    # Clean and preprocess data
    ipc_data['YEAR'] = pd.to_datetime(ipc_data['YEAR'], format='%Y').dt.year
    ipc_data['STATE/UT'] = ipc_data['STATE/UT'].str.strip()
    ipc_data['DISTRICT'] = ipc_data['DISTRICT'].str.strip()
    
    return ipc_data

# Load data
data = load_data()

# Define available crime types
crime_types = {
    'Murder': 'MURDER',
    'Rape': 'RAPE',
    'Kidnapping & Abduction': 'KIDNAPPING & ABDUCTION',
    'Robbery': 'ROBBERY',
    'Burglary': 'BURGLARY',
    'Theft': 'THEFT',
    'Riots': 'RIOTS',
    'Dowry Deaths': 'DOWRY DEATHS',
    'Assault on Women': 'ASSAULT ON WOMEN WITH INTENT TO OUTRAGE HER MODESTY',
    'Cruelty by Husband': 'CRUELTY BY HUSBAND OR HIS RELATIVES'
}

# Sidebar with improved mobile layout
with st.sidebar:
    st.title("📊 Filters")
    
    # Add a divider for better visual separation
    st.markdown("---")
    
    # Year selector with larger touch target
    st.markdown("### Select Year")
    selected_year = st.slider(
        "Year",
        min_value=int(data['YEAR'].min()),
        max_value=int(data['YEAR'].max()),
        value=int(data['YEAR'].max()),
        label_visibility="collapsed"
    )
    
    # State selector with improved mobile layout
    st.markdown("### Select State")
    selected_state = st.selectbox(
        "State",
        options=['All'] + sorted(data['STATE/UT'].unique().tolist()),
        label_visibility="collapsed"
    )
    
    # Crime type selector with improved mobile layout
    st.markdown("### Select Crime Type")
    selected_crime = st.selectbox(
        "Crime Type",
        options=list(crime_types.keys()),
        label_visibility="collapsed"
    )
    
    # Add some helpful information
    st.markdown("---")
    st.markdown("ℹ️ Use the filters above to explore crime statistics across India.")

# Main content with improved mobile layout
st.title("India Crime Analytics Dashboard")
st.markdown("### Interactive Crime Analysis Across India")

# Create tabs with improved mobile layout
tab1, tab2, tab3 = st.tabs(["🗺️ Map View", "📈 Trend Analysis", "📊 Category Analysis"])

with tab1:
    st.header(f"{selected_crime} Distribution Map")
    
    # Filter data based on selections
    filtered_data = data[data['YEAR'] == selected_year]
    if selected_state != 'All':
        filtered_data = filtered_data[filtered_data['STATE/UT'] == selected_state]
    
    # Aggregate data at state level
    state_data = filtered_data.groupby('STATE/UT')[crime_types[selected_crime]].sum().reset_index()
    
    # Create choropleth map with mobile-optimized size
    fig = px.choropleth(
        state_data,
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        featureidkey='properties.ST_NM',
        locations='STATE/UT',
        color=crime_types[selected_crime],
        color_continuous_scale='Reds',
        title=f'{selected_crime} Cases Distribution ({selected_year})'
    )
    
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=50, b=0),
        font=dict(size=14)
    )
    st.plotly_chart(fig, use_container_width=True, config={'responsive': True})

with tab2:
    st.header(f"{selected_crime} Trends Over Time")
    
    # Time series analysis
    yearly_data = data.groupby('YEAR')[crime_types[selected_crime]].sum().reset_index()
    
    fig = px.line(
        yearly_data,
        x='YEAR',
        y=crime_types[selected_crime],
        title=f'{selected_crime} Cases Trend Over Time',
        markers=True
    )
    
    fig.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=50, b=0),
        font=dict(size=14),
        xaxis=dict(tickangle=45)
    )
    st.plotly_chart(fig, use_container_width=True, config={'responsive': True})

with tab3:
    st.header("Crime Category Analysis")
    
    # Get top crime categories
    category_data = data[list(crime_types.values())].sum().reset_index()
    category_data.columns = ['Category', 'Count']
    category_data['Category'] = [k for k, v in crime_types.items()]
    
    fig = px.bar(
        category_data,
        x='Category',
        y='Count',
        title='Crime Categories Distribution',
        color='Category'
    )
    
    fig.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=50, b=0),
        font=dict(size=14),
        xaxis=dict(tickangle=45)
    )
    st.plotly_chart(fig, use_container_width=True, config={'responsive': True})

# Add footer with improved mobile layout
st.markdown("---")
st.markdown("### Data Source: National Crime Records Bureau (NCRB)")
st.markdown("This dashboard provides an interactive view of crime statistics across India. Use the filters in the sidebar to explore different aspects of the data.") 