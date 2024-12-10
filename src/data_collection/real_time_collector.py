import aiohttp
import asyncio
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import pandas as pd
import yfinance as yf
from typing import Dict, List
import json
from newsapi import NewsApiClient

load_dotenv()

class RealTimeDataCollector:
    def __init__(self):
        self.weather_api_key = os.getenv('WEATHER_API_KEY')
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.news_api = NewsApiClient(api_key=self.news_api_key)
        
        # Major tech suppliers and their stock symbols
        self.suppliers = {
            'TSM': {  # TSMC
                'name': 'Taiwan Semiconductor Manufacturing Company',
                'location': 'Hsinchu, Taiwan',
                'lat': 24.8138,
                'lon': 120.9675
            },
            'INTC': {  # Intel
                'name': 'Intel Corporation',
                'location': 'Santa Clara, USA',
                'lat': 37.3875,
                'lon': -121.9636
            },
            'SSNLF': {  # Samsung
                'name': 'Samsung Electronics',
                'location': 'Suwon, South Korea',
                'lat': 37.2636,
                'lon': 127.0286
            },
            'UMC': {  # United Microelectronics
                'name': 'United Microelectronics Corporation',
                'location': 'Hsinchu, Taiwan',
                'lat': 24.8138,
                'lon': 120.9675
            },
            'MU': {  # Micron
                'name': 'Micron Technology',
                'location': 'Boise, USA',
                'lat': 43.6150,
                'lon': -116.2023
            }
        }

    async def get_weather_data(self, lat: float, lon: float) -> Dict:
        """Fetch real-time weather data from OpenWeatherMap"""
        url = "http://api.openweathermap.org/data/2.5/onecall"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.weather_api_key,
            'units': 'metric',
            'exclude': 'minutely,hourly'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'current': data.get('current', {}),
                            'alerts': data.get('alerts', []),
                            'daily_forecast': data.get('daily', [])[:5]
                        }
        except Exception as e:
            print(f"Error fetching weather data: {e}")
        return {}

    async def get_supplier_news(self, supplier_name: str) -> List[Dict]:
        """Fetch recent news about a supplier"""
        try:
            articles = self.news_api.get_everything(
                q=supplier_name,
                language='en',
                sort_by='relevancy',
                from_param=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            )
            
            return [{
                'title': article['title'],
                'description': article['description'],
                'url': article['url'],
                'published_at': article['publishedAt'],
                'source': article['source']['name']
            } for article in articles.get('articles', [])]
        except Exception as e:
            print(f"Error fetching news data: {e}")
            return []

    def get_stock_data(self, symbol: str) -> Dict:
        """Fetch real-time stock data using yfinance"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            history = stock.history(period='1mo')
            
            return {
                'current_price': info.get('currentPrice'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('forwardPE'),
                'price_history': history['Close'].tolist(),
                'volume_history': history['Volume'].tolist(),
                'dates': history.index.strftime('%Y-%m-%d').tolist()
            }
        except Exception as e:
            print(f"Error fetching stock data: {e}")
            return {}

    async def get_world_bank_data(self, country_code: str) -> Dict:
        """Fetch economic indicators from World Bank API"""
        indicators = {
            'NY.GDP.MKTP.KD.ZG': 'gdp_growth',
            'FP.CPI.TOTL.ZG': 'inflation',
            'NE.TRD.GNFS.ZS': 'trade_percent_gdp'
        }
        
        results = {}
        base_url = "https://api.worldbank.org/v2/country"
        
        try:
            async with aiohttp.ClientSession() as session:
                for indicator_code, name in indicators.items():
                    url = f"{base_url}/{country_code}/indicator/{indicator_code}"
                    params = {'format': 'json', 'per_page': 1, 'mrnev': 1}
                    
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data and len(data) > 1 and data[1]:
                                results[name] = data[1][0].get('value')
        except Exception as e:
            print(f"Error fetching World Bank data: {e}")
        
        return results

    async def get_supplier_data(self, symbol: str) -> Dict:
        """Get comprehensive real-time data for a supplier"""
        supplier_info = self.suppliers[symbol]
        
        # Fetch all data concurrently
        weather_task = self.get_weather_data(
            supplier_info['lat'],
            supplier_info['lon']
        )
        news_task = self.get_supplier_news(supplier_info['name'])
        stock_data = self.get_stock_data(symbol)  # Not async as yfinance doesn't support it
        
        # Get country code from location
        country_code = 'TWN' if 'Taiwan' in supplier_info['location'] else \
                      'USA' if 'USA' in supplier_info['location'] else \
                      'KOR' if 'Korea' in supplier_info['location'] else 'USA'
        
        economic_task = self.get_world_bank_data(country_code)
        
        # Wait for async tasks to complete
        weather_data = await weather_task
        news_data = await news_task
        economic_data = await economic_task
        
        return {
            'supplier_info': supplier_info,
            'weather_data': weather_data,
            'news_data': news_data,
            'stock_data': stock_data,
            'economic_data': economic_data,
            'timestamp': datetime.now().isoformat()
        }

    async def get_all_suppliers_data(self) -> Dict[str, Dict]:
        """Get real-time data for all suppliers"""
        tasks = [
            self.get_supplier_data(symbol)
            for symbol in self.suppliers.keys()
        ]
        
        results = await asyncio.gather(*tasks)
        return dict(zip(self.suppliers.keys(), results))

    def calculate_risk_score(self, supplier_data: Dict) -> Dict[str, float]:
        """Calculate risk scores based on real-time data"""
        risk_scores = {}
        
        # Weather risk
        weather_data = supplier_data.get('weather_data', {})
        risk_scores['weather_risk'] = len(weather_data.get('alerts', [])) * 0.2
        
        # Financial risk
        stock_data = supplier_data.get('stock_data', {})
        if stock_data:
            price_history = stock_data.get('price_history', [])
            if price_history:
                price_volatility = pd.Series(price_history).pct_change().std()
                risk_scores['financial_risk'] = min(price_volatility * 10, 1.0)
            else:
                risk_scores['financial_risk'] = 0.5  # Default risk if no price history
        else:
            risk_scores['financial_risk'] = 0.5  # Default risk if no stock data
        
        # News sentiment risk
        news_data = supplier_data.get('news_data', [])
        risk_keywords = ['disruption', 'shortage', 'delay', 'problem', 'issue', 'risk']
        news_risk = 0
        total_articles = len(news_data)
        
        if total_articles > 0:
            risk_mentions = 0
            for article in news_data:
                title = article.get('title', '').lower() if article.get('title') else ''
                description = article.get('description', '').lower() if article.get('description') else ''
                
                if any(keyword in title or keyword in description for keyword in risk_keywords):
                    risk_mentions += 1
            
            news_risk = risk_mentions / total_articles
        
        risk_scores['news_risk'] = min(news_risk, 1.0)
        
        # Economic risk
        economic_data = supplier_data.get('economic_data', {})
        if economic_data:
            inflation_risk = min(max(economic_data.get('inflation', 0), 0) / 10, 1.0)
            gdp_risk = 1 - min(max(economic_data.get('gdp_growth', 0), 0) / 10, 1.0)
            risk_scores['economic_risk'] = (inflation_risk + gdp_risk) / 2
        else:
            risk_scores['economic_risk'] = 0.5  # Default risk if no economic data
        
        # Calculate overall risk (average of all available risk scores)
        available_risks = [score for score in risk_scores.values() if score is not None]
        risk_scores['overall_risk'] = sum(available_risks) / len(available_risks) if available_risks else 0.5
        
        return risk_scores

async def get_real_time_data():
    """Helper function to get all real-time data"""
    collector = RealTimeDataCollector()
    return await collector.get_all_suppliers_data() 