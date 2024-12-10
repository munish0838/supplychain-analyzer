import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static
import numpy as np
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Supply Chain Risk Monitor",
    page_icon="🌐",
    layout="wide"
)

# Title and description
st.title("Supply Chain Risk Monitoring System")

# Sidebar
st.sidebar.title("Controls")
risk_threshold = st.sidebar.slider("Risk Threshold", 0, 100, 50)
selected_view = st.sidebar.selectbox(
    "Select View",
    ["Global Overview", "Supplier Analysis", "Component Risks", "Alerts"]
)

# Main content
def main():
    # Tabs for different views
    if selected_view == "Global Overview":
        show_global_overview()
    elif selected_view == "Supplier Analysis":
        show_supplier_analysis()
    elif selected_view == "Component Risks":
        show_component_risks()
    else:
        show_alerts()

def show_global_overview():
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Global Risk Map")
        # Create a sample map
        m = folium.Map(location=[20, 0], zoom_start=2)
        # Add sample markers
        sample_locations = [
            {"lat": 40.7128, "lon": -74.0060, "risk": 75},
            {"lat": 31.2304, "lon": 121.4737, "risk": 45},
            {"lat": 51.5074, "lon": -0.1278, "risk": 30},
        ]
        for loc in sample_locations:
            folium.CircleMarker(
                location=[loc["lat"], loc["lon"]],
                radius=loc["risk"]/5,
                color="red" if loc["risk"] > risk_threshold else "green",
                popup=f"Risk Score: {loc['risk']}",
                fill=True
            ).add_to(m)
        folium_static(m)
    
    with col2:
        st.subheader("Risk Distribution")
        # Sample risk data
        risk_data = pd.DataFrame({
            'Category': ['Weather', 'Political', 'Economic', 'Supply', 'Demand'],
            'Risk Score': [65, 45, 80, 30, 50]
        })
        fig = px.bar(risk_data, x='Category', y='Risk Score',
                    color='Risk Score',
                    color_continuous_scale=['green', 'yellow', 'red'])
        st.plotly_chart(fig)

def show_supplier_analysis():
    st.subheader("Supplier Risk Analysis")
    # Sample supplier data
    supplier_data = pd.DataFrame({
        'Supplier': [f'Supplier {i}' for i in range(1, 6)],
        'Risk Score': np.random.randint(0, 100, 5),
        'Location': ['USA', 'China', 'Germany', 'Japan', 'India'],
        'Components': np.random.randint(5, 50, 5)
    })
    st.dataframe(supplier_data)
    
    # Supplier risk distribution
    fig = px.scatter(supplier_data, x='Components', y='Risk Score',
                    color='Location', size='Risk Score',
                    hover_data=['Supplier'])
    st.plotly_chart(fig)

def show_component_risks():
    st.subheader("Component Risk Analysis")
    # Sample component data
    component_data = pd.DataFrame({
        'Component': [f'Component {i}' for i in range(1, 8)],
        'Stock Level': np.random.randint(100, 1000, 7),
        'Lead Time': np.random.randint(10, 60, 7),
        'Risk Level': np.random.randint(0, 100, 7)
    })
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("Component Inventory Status")
        st.dataframe(component_data)
    
    with col2:
        fig = px.scatter(component_data, x='Lead Time', y='Stock Level',
                        color='Risk Level', size='Risk Level',
                        hover_data=['Component'])
        st.plotly_chart(fig)

def show_alerts():
    st.subheader("Active Alerts")
    # Sample alerts
    alerts = pd.DataFrame({
        'Timestamp': [datetime.now() - timedelta(hours=i) for i in range(5)],
        'Type': ['Weather Warning', 'Supply Shortage', 'Price Surge',
                'Delivery Delay', 'Quality Issue'],
        'Severity': ['High', 'Medium', 'High', 'Low', 'Medium'],
        'Description': [
            'Hurricane warning in supplier region',
            'Component X stock below threshold',
            'Raw material prices increased by 30%',
            'Port congestion causing delays',
            'Quality control failed for recent batch'
        ]
    })
    
    # Display alerts with color coding
    for _, alert in alerts.iterrows():
        severity_color = {
            'High': 'red',
            'Medium': 'orange',
            'Low': 'green'
        }[alert['Severity']]
        
        st.markdown(
            f"""
            <div style='padding:10px; border-left:5px solid {severity_color}; margin:10px 0;'>
                <strong>{alert['Timestamp'].strftime('%Y-%m-%d %H:%M')}</strong><br>
                <strong style='color:{severity_color};'>{alert['Type']}</strong> - {alert['Severity']}<br>
                {alert['Description']}
            </div>
            """,
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main() 