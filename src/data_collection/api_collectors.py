import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from newsapi import NewsApiClient
import xml.etree.ElementTree as ET
import asyncio
import aiohttp
import json

load_dotenv()

class WeatherCollector:
    def __init__(self):
        self.api_key = os.getenv('WEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    async def get_weather_data(self, lat: float, lon: float) -> Dict:
        """Get weather data and alerts for a specific location"""
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': 'metric',
            'exclude': 'minutely,hourly'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/onecall", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Process weather conditions
                        alerts = data.get('alerts', [])
                        daily = data.get('daily', [])
                        current = data.get('current', {})
                        
                        risk_condition = 'normal'
                        if alerts:
                            risk_condition = 'extreme_weather'
                        elif any(d.get('weather', [{}])[0].get('main', '').lower() in 
                               ['thunderstorm', 'tornado', 'hurricane'] for d in daily[:3]):
                            risk_condition = 'extreme_weather'
                        elif current.get('temp', 20) > 35 or current.get('temp', 20) < 0:
                            risk_condition = 'extreme_weather'
                        
                        return {
                            'condition': risk_condition,
                            'temperature': current.get('temp'),
                            'alerts': alerts,
                            'forecast': daily[:5],
                            'description': current.get('weather', [{}])[0].get('description')
                        }
            
            return {'condition': 'normal'}
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return {'condition': 'normal'}

class DisasterCollector:
    def __init__(self):
        self.gdacs_url = "https://www.gdacs.org/xml/rss.xml"
        self.nasa_eonet_url = "https://eonet.gsfc.nasa.gov/api/v3/events"
    
    async def get_disaster_alerts(self) -> List[Dict]:
        """Get disaster alerts from GDACS and NASA EONET"""
        alerts = []
        
        try:
            # GDACS Alerts
            async with aiohttp.ClientSession() as session:
                async with session.get(self.gdacs_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        root = ET.fromstring(content)
                        for item in root.findall('.//item'):
                            alerts.append({
                                'source': 'GDACS',
                                'title': item.find('title').text,
                                'description': item.find('description').text,
                                'date': item.find('pubDate').text
                            })
                
                # NASA EONET Events
                async with session.get(self.nasa_eonet_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        for event in data.get('events', []):
                            alerts.append({
                                'source': 'NASA EONET',
                                'title': event.get('title'),
                                'description': event.get('description'),
                                'date': event.get('geometry', [{}])[0].get('date')
                            })
        
        except Exception as e:
            print(f"Error fetching disaster alerts: {e}")
        
        return alerts

class TradeDataCollector:
    def __init__(self):
        self.world_bank_base_url = "https://api.worldbank.org/v2"
        self.comtrade_base_url = "https://comtrade.un.org/api/get"
        self.indicators = {
            'trade': 'NE.TRD.GNFS.ZS',
            'manufacturing': 'NV.IND.MANF.ZS',
            'logistics': 'LP.LPI.OVRL.XQ'
        }
    
    async def get_trade_data(self, country_code: str) -> Dict:
        """Get trade and economic indicators from World Bank"""
        data = {}
        
        try:
            async with aiohttp.ClientSession() as session:
                for indicator_name, indicator_code in self.indicators.items():
                    url = f"{self.world_bank_base_url}/country/{country_code}/indicator/{indicator_code}"
                    params = {'format': 'json', 'per_page': 1, 'mrnev': 1}
                    
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            result = await response.json()
                            if result and len(result) > 1 and result[1]:
                                data[indicator_name] = result[1][0].get('value')
        
        except Exception as e:
            print(f"Error fetching trade data: {e}")
        
        return data
    
    async def get_comtrade_data(self, reporter: str, partner: str, commodity_code: str) -> Dict:
        """Get trade flow data from UN Comtrade"""
        params = {
            'max': 1,
            'type': 'C',
            'freq': 'M',
            'px': 'HS',
            'ps': 'now',
            'r': reporter,
            'p': partner,
            'cc': commodity_code,
            'fmt': 'json'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.comtrade_base_url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
        except Exception as e:
            print(f"Error fetching Comtrade data: {e}")
        
        return {}

class NewsCollector:
    def __init__(self):
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.news_api = NewsApiClient(api_key=self.news_api_key)
        self.gta_url = "https://www.globaltradealert.org/json_feed"
    
    async def get_supply_chain_news(self, location: str, days: int = 7) -> List[Dict]:
        """Get supply chain related news from multiple sources"""
        news_items = []
        
        try:
            # NewsAPI
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            query = f"supply chain OR logistics OR manufacturing {location}"
            
            articles = self.news_api.get_everything(
                q=query,
                from_param=from_date,
                language='en',
                sort_by='relevancy'
            )
            
            for article in articles.get('articles', []):
                news_items.append({
                    'source': 'NewsAPI',
                    'title': article['title'],
                    'description': article['description'],
                    'url': article['url'],
                    'published_at': article['publishedAt'],
                    'source_name': article['source']['name']
                })
            
            # Global Trade Alert
            async with aiohttp.ClientSession() as session:
                async with session.get(self.gta_url) as response:
                    if response.status == 200:
                        gta_data = await response.json()
                        for item in gta_data:
                            if location.lower() in item.get('title', '').lower():
                                news_items.append({
                                    'source': 'GTA',
                                    'title': item.get('title'),
                                    'description': item.get('description'),
                                    'url': item.get('url'),
                                    'published_at': item.get('published_date'),
                                    'source_name': 'Global Trade Alert'
                                })
        
        except Exception as e:
            print(f"Error fetching news data: {e}")
        
        return news_items

async def collect_location_data(lat: float, lon: float, location_name: str, country_code: str) -> Dict:
    """Collect all relevant data for a specific location"""
    weather_collector = WeatherCollector()
    news_collector = NewsCollector()
    disaster_collector = DisasterCollector()
    trade_collector = TradeDataCollector()
    
    # Gather all data concurrently
    weather_task = asyncio.create_task(weather_collector.get_weather_data(lat, lon))
    news_task = asyncio.create_task(news_collector.get_supply_chain_news(location_name))
    disaster_task = asyncio.create_task(disaster_collector.get_disaster_alerts())
    trade_task = asyncio.create_task(trade_collector.get_trade_data(country_code))
    
    # Wait for all tasks to complete
    weather_data = await weather_task
    news_data = await news_task
    disaster_data = await disaster_task
    trade_data = await trade_task
    
    return {
        'weather': weather_data,
        'news': news_data,
        'disasters': disaster_data,
        'trade': trade_data,
        'timestamp': datetime.now().isoformat()
    } 