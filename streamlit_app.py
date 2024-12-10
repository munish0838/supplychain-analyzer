import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
import numpy as np
from datetime import datetime, timedelta
import asyncio
from src.data_collection.real_time_collector import RealTimeDataCollector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize data collector
data_collector = RealTimeDataCollector()

# Page config
st.set_page_config(
    page_title="Supply Chain Risk Monitor",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stAlert {
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
    }
    .risk-high {
        color: #ff4b4b;
        font-weight: bold;
    }
    .risk-medium {
        color: #ffa600;
        font-weight: bold;
    }
    .risk-low {
        color: #00cc96;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .feature-card {
        background-color: #ffffff;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .feature-card h3 {
        color: #0066cc;
        margin-bottom: 1rem;
        font-size: 1.2rem;
    }
    .feature-card ul {
        color: #424242;
        margin-left: 1.5rem;
        margin-bottom: 0;
    }
    .feature-card li {
        margin-bottom: 0.5rem;
    }
    .data-source-card {
        background-color: #ffffff;
        border-left: 4px solid #0066cc;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .data-source-card h4 {
        color: #0066cc;
        margin-bottom: 1rem;
        font-size: 1.1rem;
    }
    .data-source-card p {
        color: #424242;
        margin-bottom: 0.5rem;
    }
    .data-source-card ul {
        color: #424242;
        margin-left: 1.5rem;
        margin-bottom: 0;
    }
    .data-source-card li {
        margin-bottom: 0.3rem;
    }
    .methodology-table {
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .methodology-table th {
        background-color: #f0f2f6;
        padding: 0.5rem;
    }
    .methodology-table td {
        padding: 0.5rem;
    }
    .section-header {
        color: #0066cc;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #0066cc;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Select View",
    ["Getting Started", "Dashboard Overview", "Supplier Analysis", "Market Data", "Risk Assessment", "Alerts"]
)

# Add auto-refresh option
if page != "Getting Started":
    auto_refresh = st.sidebar.checkbox("Auto-refresh data (30s)", value=False)
    if auto_refresh:
        st.empty()
        st.experimental_rerun()

def show_getting_started():
    """Show the getting started page with comprehensive explanation"""
    st.title("🌐 Supply Chain Risk Monitoring System")
    
    # Introduction
    st.markdown("""
        <div style="padding: 1rem; background-color: #f8f9fa; border-radius: 5px; margin-bottom: 2rem;">
            <h2 style="color: #0066cc; margin-bottom: 1rem;">Welcome to SCRMS</h2>
            <p style="color: #424242; font-size: 1.1rem;">
                The Supply Chain Risk Monitoring System (SCRMS) is an enterprise-grade solution for real-time 
                supply chain risk assessment and monitoring. This system helps you identify, analyze, and respond to 
                potential disruptions across your global supply chain network.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Key Features
    st.markdown('<h2 class="section-header">🎯 Key Features</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="feature-card">
                <h3>🗺️ Global Risk Mapping</h3>
                <ul>
                    <li>Real-time supplier location monitoring</li>
                    <li>Geographic risk visualization</li>
                    <li>Interactive risk heat maps</li>
                    <li>Regional disruption tracking</li>
                </ul>
            </div>
            
            <div class="feature-card">
                <h3>📊 Market Intelligence</h3>
                <ul>
                    <li>Live stock price monitoring</li>
                    <li>Financial health indicators</li>
                    <li>Market trend analysis</li>
                    <li>Comparative performance metrics</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="feature-card">
                <h3>⚠️ Risk Assessment</h3>
                <ul>
                    <li>Multi-factor risk scoring</li>
                    <li>Predictive risk analytics</li>
                    <li>Customizable risk thresholds</li>
                    <li>Historical risk trending</li>
                </ul>
            </div>
            
            <div class="feature-card">
                <h3>🔔 Real-time Alerts</h3>
                <ul>
                    <li>Weather event notifications</li>
                    <li>Market volatility alerts</li>
                    <li>News and media monitoring</li>
                    <li>Customizable alert thresholds</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    # Data Sources
    st.markdown('<h2 class="section-header">📡 Real-time Data Sources</h2>', unsafe_allow_html=True)
    st.markdown("""
        <p style="color: #424242; margin-bottom: 1.5rem;">
            The system integrates data from multiple reliable sources to provide comprehensive risk assessment:
        </p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="data-source-card">
                <h4>🌤️ Weather Data</h4>
                <p>OpenWeatherMap API provides:</p>
                <ul>
                    <li>Current conditions</li>
                    <li>Weather alerts</li>
                    <li>5-day forecasts</li>
                    <li>Historical weather data</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="data-source-card">
                <h4>📰 News & Events</h4>
                <p>NewsAPI integration delivers:</p>
                <ul>
                    <li>Global news coverage</li>
                    <li>Industry-specific news</li>
                    <li>Company announcements</li>
                    <li>Market updates</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="data-source-card">
                <h4>📈 Market Data</h4>
                <p>Yahoo Finance provides:</p>
                <ul>
                    <li>Real-time stock prices</li>
                    <li>Financial metrics</li>
                    <li>Market indicators</li>
                    <li>Trading volumes</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    # Risk Assessment Methodology
    st.markdown('<h2 class="section-header">🎯 Risk Assessment Methodology</h2>', unsafe_allow_html=True)
    st.markdown("""
        <p style="color: #424242; margin-bottom: 1.5rem;">
            Our risk assessment engine analyzes multiple factors to provide comprehensive risk scores:
        </p>
    """, unsafe_allow_html=True)
    
    methodology_data = pd.DataFrame({
        'Risk Factor': ['Weather Risk', 'Financial Risk', 'News Sentiment', 'Economic Risk'],
        'Weight': [25, 30, 25, 20],
        'Data Points': ['Weather alerts, Natural disasters', 'Stock volatility, Market cap', 
                       'News sentiment, Media coverage', 'GDP growth, Inflation rate']
    })
    
    st.markdown('<div class="methodology-table">', unsafe_allow_html=True)
    st.table(methodology_data)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Getting Started Guide
    st.markdown('<h2 class="section-header">🚀 Getting Started</h2>', unsafe_allow_html=True)
    st.markdown("""
        <div style="color: #424242;">
            <p>Follow these steps to start monitoring your supply chain:</p>
            
            <ol>
                <li><strong>Dashboard Overview</strong>: Get a global view of your supply chain risks
                    <ul>
                        <li>View the interactive risk map</li>
                        <li>Monitor key performance indicators</li>
                        <li>Track real-time alerts</li>
                    </ul>
                </li>
                
                <li><strong>Supplier Analysis</strong>: Dive deep into supplier performance
                    <ul>
                        <li>Analyze individual supplier risks</li>
                        <li>Track historical performance</li>
                        <li>Monitor supplier-specific news</li>
                    </ul>
                </li>
                
                <li><strong>Market Data</strong>: Stay updated with market conditions
                    <ul>
                        <li>Track stock performance</li>
                        <li>Monitor market trends</li>
                        <li>Compare supplier metrics</li>
                    </ul>
                </li>
                
                <li><strong>Risk Assessment</strong>: Evaluate comprehensive risk scores
                    <ul>
                        <li>View detailed risk breakdowns</li>
                        <li>Analyze risk factors</li>
                        <li>Get actionable insights</li>
                    </ul>
                </li>
                
                <li><strong>Alerts</strong>: Stay informed about critical events
                    <ul>
                        <li>Configure alert thresholds</li>
                        <li>Receive real-time notifications</li>
                        <li>Track alert history</li>
                    </ul>
                </li>
            </ol>
        </div>
    """, unsafe_allow_html=True)
    
    # System Requirements
    st.markdown('<h2 class="section-header">⚙️ System Requirements</h2>', unsafe_allow_html=True)
    st.markdown("""
        <div class="feature-card">
            <p style="color: #424242;">To use all features of the system, ensure you have:</p>
            
            <ol style="color: #424242;">
                <li><strong>API Keys</strong> configured in `.env` file:
                    <ul>
                        <li>OpenWeatherMap API key</li>
                        <li>NewsAPI key</li>
                    </ul>
                </li>
                <li><strong>System Requirements</strong>:
                    <ul>
                        <li>Internet connection for real-time data</li>
                        <li>Modern web browser</li>
                        <li>System memory: 4GB minimum</li>
                    </ul>
                </li>
            </ol>
        </div>
    """, unsafe_allow_html=True)
    
    # Help & Support
    st.markdown('<h2 class="section-header">❓ Help & Support</h2>', unsafe_allow_html=True)
    st.markdown("""
        <div class="feature-card">
            <p style="color: #424242;">For additional help:</p>
            
            <ul style="color: #424242;">
                <li>Check the documentation</li>
                <li>Contact system administrator</li>
                <li>Report issues on GitHub</li>
                <li>Join our community forum</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

def format_risk_score(score):
    """Format risk score with color coding"""
    if score >= 0.7:
        return f'<span class="risk-high">{score:.2f}</span>'
    elif score >= 0.4:
        return f'<span class="risk-medium">{score:.2f}</span>'
    else:
        return f'<span class="risk-low">{score:.2f}</span>'

async def show_dashboard():
    """Show main dashboard with real-time data"""
    # Fetch real-time data
    with st.spinner("Fetching real-time data..."):
        suppliers_data = await data_collector.get_all_suppliers_data()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Global Supply Chain Risk Map")
        m = folium.Map(location=[30, 0], zoom_start=2)
        
        # Add suppliers to map with real-time data
        for symbol, data in suppliers_data.items():
            supplier_info = data['supplier_info']
            risk_scores = data_collector.calculate_risk_score(data)
            
            color = 'red' if risk_scores['overall_risk'] > 0.7 else \
                   'orange' if risk_scores['overall_risk'] > 0.4 else 'green'
            
            # Create detailed popup
            weather = data['weather_data'].get('current', {})
            stock = data['stock_data']
            popup_html = f"""
                <b>{supplier_info['name']}</b><br>
                Location: {supplier_info['location']}<br>
                Risk Score: {risk_scores['overall_risk']:.2f}<br>
                Weather: {weather.get('temp', 'N/A')}°C<br>
                Stock Price: ${stock.get('current_price', 'N/A')}<br>
                Market Cap: ${stock.get('market_cap', 0)/1e9:.2f}B
            """
            
            folium.CircleMarker(
                location=[supplier_info['lat'], supplier_info['lon']],
                radius=risk_scores['overall_risk'] * 20,
                popup=folium.Popup(popup_html, max_width=300),
                color=color,
                fill=True
            ).add_to(m)
        
        folium_static(m)
    
    with col2:
        st.subheader("Risk Distribution")
        # Calculate average risk scores
        all_risks = []
        for data in suppliers_data.values():
            risks = data_collector.calculate_risk_score(data)
            all_risks.append(risks)
        
        avg_risks = pd.DataFrame(all_risks).mean()
        risk_data = pd.DataFrame({
            'Category': avg_risks.index,
            'Risk Score': avg_risks.values
        })
        
        fig = px.bar(risk_data, x='Category', y='Risk Score',
                    color='Risk Score',
                    color_continuous_scale=['green', 'yellow', 'red'])
        st.plotly_chart(fig)
    
    # Key Metrics
    st.subheader("Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Active Suppliers",
            len(suppliers_data),
            "Real-time monitoring"
        )
    
    # Calculate high-risk suppliers
    high_risk = sum(1 for data in suppliers_data.values()
                   if data_collector.calculate_risk_score(data)['overall_risk'] > 0.7)
    with col2:
        st.metric(
            "High Risk Suppliers",
            high_risk,
            f"{(high_risk/len(suppliers_data))*100:.0f}% of total"
        )
    
    # Calculate average stock performance
    avg_stock_change = np.mean([
        (data['stock_data'].get('price_history', [0])[-1] /
         data['stock_data'].get('price_history', [1])[0] - 1) * 100
        for data in suppliers_data.values()
        if data['stock_data'].get('price_history')
    ])
    with col3:
        st.metric(
            "Avg Stock Performance",
            f"{avg_stock_change:.1f}%",
            "30-day change"
        )
    
    # Count active weather alerts
    total_alerts = sum(
        len(data['weather_data'].get('alerts', []))
        for data in suppliers_data.values()
    )
    with col4:
        st.metric(
            "Active Weather Alerts",
            total_alerts,
            "Across all locations"
        )

async def show_supplier_analysis():
    """Show supplier analysis with real-time data"""
    with st.spinner("Fetching real-time data..."):
        suppliers_data = await data_collector.get_all_suppliers_data()
    
    # Supplier selector
    selected_symbol = st.selectbox(
        "Select Supplier",
        list(suppliers_data.keys()),
        format_func=lambda x: suppliers_data[x]['supplier_info']['name']
    )
    
    supplier_data = suppliers_data[selected_symbol]
    risk_scores = data_collector.calculate_risk_score(supplier_data)
    
    # Display supplier overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Supplier Overview")
        st.markdown(f"""
            **Company**: {supplier_data['supplier_info']['name']}  
            **Location**: {supplier_data['supplier_info']['location']}  
            **Overall Risk Score**: {format_risk_score(risk_scores['overall_risk'])}
        """, unsafe_allow_html=True)
        
        # Stock performance
        stock_data = supplier_data['stock_data']
        if stock_data and stock_data.get('price_history'):
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=stock_data['dates'],
                y=stock_data['price_history'],
                name='Stock Price'
            ))
            fig.update_layout(title='Stock Performance (30 Days)')
            st.plotly_chart(fig)
    
    with col2:
        st.subheader("Risk Breakdown")
        risk_df = pd.DataFrame({
            'Risk Category': risk_scores.keys(),
            'Risk Score': risk_scores.values()
        })
        fig = px.bar(risk_df, x='Risk Category', y='Risk Score',
                    color='Risk Score',
                    color_continuous_scale=['green', 'yellow', 'red'])
        st.plotly_chart(fig)
    
    # News Feed
    st.subheader("Recent News")
    for article in supplier_data['news_data'][:5]:
        st.markdown(f"""
            <div style='padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin: 5px 0;'>
                <h4>{article['title']}</h4>
                <p>{article['description']}</p>
                <small>Source: {article['source']} | {article['published_at']}</small>
            </div>
        """, unsafe_allow_html=True)

async def show_market_data():
    """Show market data analysis"""
    with st.spinner("Fetching real-time data..."):
        suppliers_data = await data_collector.get_all_suppliers_data()
    
    st.subheader("Market Overview")
    
    # Create market summary dataframe
    market_data = []
    for symbol, data in suppliers_data.items():
        stock_data = data['stock_data']
        if stock_data:
            market_data.append({
                'Company': data['supplier_info']['name'],
                'Symbol': symbol,
                'Price': stock_data.get('current_price', 'N/A'),
                'Market Cap ($B)': stock_data.get('market_cap', 0) / 1e9,
                'P/E Ratio': stock_data.get('pe_ratio', 'N/A'),
                '30d Volume': np.mean(stock_data.get('volume_history', [0]))
            })
    
    market_df = pd.DataFrame(market_data)
    st.dataframe(market_df)
    
    # Stock price comparison
    st.subheader("Stock Price Comparison")
    fig = go.Figure()
    for symbol, data in suppliers_data.items():
        stock_data = data['stock_data']
        if stock_data and stock_data.get('price_history'):
            # Normalize prices to percentage change
            prices = np.array(stock_data['price_history'])
            normalized_prices = (prices / prices[0] - 1) * 100
            
            fig.add_trace(go.Scatter(
                x=stock_data['dates'],
                y=normalized_prices,
                name=symbol
            ))
    
    fig.update_layout(
        title='30-Day Price Performance (%)',
        yaxis_title='Price Change (%)'
    )
    st.plotly_chart(fig)

async def show_risk_assessment():
    """Show risk assessment with real-time data"""
    with st.spinner("Fetching real-time data..."):
        suppliers_data = await data_collector.get_all_suppliers_data()
    
    st.subheader("Risk Assessment")
    
    # Create risk summary
    risk_summary = []
    for symbol, data in suppliers_data.items():
        risk_scores = data_collector.calculate_risk_score(data)
        risk_summary.append({
            'Company': data['supplier_info']['name'],
            'Location': data['supplier_info']['location'],
            'Overall Risk': risk_scores['overall_risk'],
            'Weather Risk': risk_scores['weather_risk'],
            'Financial Risk': risk_scores.get('financial_risk', 0),
            'News Risk': risk_scores['news_risk'],
            'Economic Risk': risk_scores.get('economic_risk', 0)
        })
    
    risk_df = pd.DataFrame(risk_summary)
    
    # Display risk matrix
    st.subheader("Risk Matrix")
    fig = px.scatter(risk_df,
                    x='Financial Risk',
                    y='Weather Risk',
                    size='Overall Risk',
                    color='Overall Risk',
                    hover_data=['Company'],
                    color_continuous_scale=['green', 'yellow', 'red'])
    
    fig.update_layout(
        title='Risk Matrix (Financial vs Weather Risk)',
        xaxis_title='Financial Risk',
        yaxis_title='Weather Risk'
    )
    st.plotly_chart(fig)
    
    # Display detailed risk table
    st.subheader("Detailed Risk Assessment")
    st.dataframe(risk_df)

async def show_alerts():
    """Show alerts based on real-time data"""
    with st.spinner("Fetching real-time data..."):
        suppliers_data = await data_collector.get_all_suppliers_data()
    
    st.subheader("Active Alerts")
    
    # Generate alerts from real-time data
    alerts = []
    
    # Weather alerts
    for symbol, data in suppliers_data.items():
        company = data['supplier_info']['name']
        weather_alerts = data['weather_data'].get('alerts', [])
        for alert in weather_alerts:
            alerts.append({
                'timestamp': datetime.now(),
                'type': 'Weather Alert',
                'severity': 'High',
                'description': f"Weather alert for {company}: {alert.get('event', 'Unknown event')}"
            })
    
    # Risk alerts
    for symbol, data in suppliers_data.items():
        risk_scores = data_collector.calculate_risk_score(data)
        if risk_scores['overall_risk'] > 0.7:
            alerts.append({
                'timestamp': datetime.now(),
                'type': 'High Risk Alert',
                'severity': 'High',
                'description': f"{data['supplier_info']['name']} has high risk score: {risk_scores['overall_risk']:.2f}"
            })
    
    # Stock alerts
    for symbol, data in suppliers_data.items():
        stock_data = data['stock_data']
        if stock_data and stock_data.get('price_history'):
            price_change = (stock_data['price_history'][-1] / stock_data['price_history'][0] - 1) * 100
            if abs(price_change) > 5:
                alerts.append({
                    'timestamp': datetime.now(),
                    'type': 'Stock Price Alert',
                    'severity': 'Medium',
                    'description': f"{data['supplier_info']['name']} stock price changed by {price_change:.1f}% in 30 days"
                })
    
    # Display alerts
    if not alerts:
        st.info("No active alerts at the moment.")
    else:
        for alert in alerts:
            severity_color = {
                'High': 'red',
                'Medium': 'orange',
                'Low': 'green'
            }[alert['severity']]
            
            st.markdown(f"""
                <div style='padding:10px; border-left:5px solid {severity_color}; margin:10px 0;'>
                    <strong>{alert['timestamp'].strftime('%Y-%m-%d %H:%M')}</strong><br>
                    <strong style='color:{severity_color};'>{alert['type']}</strong> - {alert['severity']}<br>
                    {alert['description']}
                </div>
            """, unsafe_allow_html=True)

# Display selected page
if page == "Getting Started":
    show_getting_started()
elif page == "Dashboard Overview":
    asyncio.run(show_dashboard())
elif page == "Supplier Analysis":
    asyncio.run(show_supplier_analysis())
elif page == "Market Data":
    asyncio.run(show_market_data())
elif page == "Risk Assessment":
    asyncio.run(show_risk_assessment())
else:
    asyncio.run(show_alerts())

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        Supply Chain Risk Monitoring System (SCRMS) v1.0<br>
        Last updated: {}<br>
        Data sources: OpenWeatherMap, NewsAPI, Yahoo Finance, World Bank
    </div>
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True) 