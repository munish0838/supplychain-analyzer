import numpy as np
from sklearn.preprocessing import MinMaxScaler
from typing import Dict, List, Union
import pandas as pd
from datetime import datetime, timedelta

class RiskScorer:
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.weights = {
            'weather': 0.2,
            'political': 0.15,
            'economic': 0.25,
            'supply': 0.25,
            'demand': 0.15
        }
        
        self.disaster_severity_weights = {
            'earthquake': 1.0,
            'tsunami': 1.0,
            'hurricane': 0.9,
            'flood': 0.8,
            'storm': 0.7,
            'drought': 0.6,
            'wildfire': 0.8
        }
    
    def calculate_weather_risk(self, weather_data: Dict) -> float:
        """Calculate weather-related risk score"""
        base_risk = 0.1  # Default low risk
        
        # Check for active alerts
        if weather_data.get('alerts', []):
            base_risk = 0.8
        
        # Check current condition
        risk_factors = {
            'extreme_weather': 1.0,
            'storm_warning': 0.7,
            'flood_risk': 0.8,
            'normal': 0.1
        }
        condition_risk = risk_factors.get(weather_data.get('condition', 'normal'), 0.1)
        
        # Check forecast
        forecast_risk = 0.0
        for day in weather_data.get('forecast', []):
            weather_main = day.get('weather', [{}])[0].get('main', '').lower()
            if weather_main in ['thunderstorm', 'tornado', 'hurricane']:
                forecast_risk = max(forecast_risk, 0.9)
            elif weather_main in ['rain', 'snow', 'storm']:
                forecast_risk = max(forecast_risk, 0.6)
        
        return max(base_risk, condition_risk, forecast_risk)
    
    def calculate_disaster_risk(self, disaster_data: List[Dict]) -> float:
        """Calculate disaster-related risk score"""
        if not disaster_data:
            return 0.0
        
        max_risk = 0.0
        recent_disasters = [
            d for d in disaster_data 
            if (datetime.now() - datetime.fromisoformat(d['date'].replace('Z', '+00:00'))).days <= 7
        ]
        
        for disaster in recent_disasters:
            title_lower = disaster['title'].lower()
            for disaster_type, weight in self.disaster_severity_weights.items():
                if disaster_type in title_lower:
                    max_risk = max(max_risk, weight)
                    break
        
        return max_risk
    
    def calculate_trade_risk(self, trade_data: Dict) -> float:
        """Calculate trade-related risk score"""
        if not trade_data:
            return 0.5  # Default moderate risk if no data
        
        # Normalize and weight different indicators
        trade_risk = 1 - (trade_data.get('trade', 50) / 100)  # Higher trade % = lower risk
        manufacturing_risk = 1 - (trade_data.get('manufacturing', 50) / 100)
        logistics_risk = 1 - (trade_data.get('logistics', 2.5) / 5)  # LPI is 1-5
        
        # Weight the components
        weighted_risk = (
            trade_risk * 0.3 +
            manufacturing_risk * 0.3 +
            logistics_risk * 0.4
        )
        
        return min(weighted_risk, 1.0)
    
    def calculate_news_sentiment_risk(self, news_data: List[Dict]) -> float:
        """Calculate risk based on news sentiment"""
        if not news_data:
            return 0.0
        
        # Risk keywords and their weights
        risk_keywords = {
            'disruption': 0.8,
            'shortage': 0.7,
            'delay': 0.6,
            'crisis': 0.8,
            'strike': 0.7,
            'shutdown': 0.8,
            'bankruptcy': 0.9,
            'recall': 0.7,
            'accident': 0.6,
            'investigation': 0.5
        }
        
        max_risk = 0.0
        recent_news = news_data[:10]  # Focus on most recent/relevant news
        
        for news in recent_news:
            title = news['title'].lower()
            description = news.get('description', '').lower()
            
            for keyword, weight in risk_keywords.items():
                if keyword in title:
                    max_risk = max(max_risk, weight)
                elif keyword in description:
                    max_risk = max(max_risk, weight * 0.7)  # Lower weight for description matches
        
        return max_risk
    
    def calculate_political_risk(self, news_data: List[Dict], trade_data: Dict) -> float:
        """Calculate political risk score"""
        # Base risk from trade data
        base_risk = self.calculate_trade_risk(trade_data) * 0.5
        
        # Additional risk from news about political issues
        political_keywords = {
            'tariff': 0.7,
            'sanction': 0.9,
            'trade war': 0.8,
            'regulation': 0.6,
            'policy change': 0.5,
            'restriction': 0.7,
            'compliance': 0.6
        }
        
        news_risk = 0.0
        for news in news_data:
            title = news['title'].lower()
            description = news.get('description', '').lower()
            
            for keyword, weight in political_keywords.items():
                if keyword in title or keyword in description:
                    news_risk = max(news_risk, weight)
        
        return max(base_risk, news_risk)
    
    def calculate_economic_risk(self, trade_data: Dict) -> float:
        """Calculate economic risk score"""
        return self.calculate_trade_risk(trade_data)
    
    def calculate_supply_risk(self, supply_data: Dict) -> float:
        """Calculate supply-related risk score"""
        inventory_level = supply_data.get('inventory_level', 50)
        lead_time = supply_data.get('lead_time', 30)
        supplier_reliability = supply_data.get('supplier_reliability', 0.5)
        
        inventory_risk = (100 - inventory_level) / 100
        lead_time_risk = min(lead_time / 60, 1.0)  # Normalize to 60 days
        reliability_risk = 1 - supplier_reliability
        
        return (inventory_risk * 0.4 + lead_time_risk * 0.3 + reliability_risk * 0.3)
    
    def calculate_demand_risk(self, demand_data: Dict) -> float:
        """Calculate demand-related risk score"""
        forecast_accuracy = demand_data.get('forecast_accuracy', 0.7)
        demand_volatility = demand_data.get('demand_volatility', 0.3)
        
        accuracy_risk = 1 - forecast_accuracy
        return (accuracy_risk * 0.6 + demand_volatility * 0.4)
    
    def calculate_overall_risk(self, data: Dict) -> Dict[str, float]:
        """Calculate overall risk score and component scores"""
        # Calculate component risks
        weather_risk = self.calculate_weather_risk(data.get('weather', {}))
        disaster_risk = self.calculate_disaster_risk(data.get('disasters', []))
        news_risk = self.calculate_news_sentiment_risk(data.get('news', []))
        trade_risk = self.calculate_trade_risk(data.get('trade', {}))
        
        # Combine weather and disaster risks
        environmental_risk = max(weather_risk, disaster_risk)
        
        risk_scores = {
            'weather': environmental_risk,
            'political': self.calculate_political_risk(data.get('news', []), data.get('trade', {})),
            'economic': self.calculate_economic_risk(data.get('trade', {})),
            'supply': self.calculate_supply_risk(data.get('supply', {})),
            'demand': self.calculate_demand_risk(data.get('demand', {})),
            'news_sentiment': news_risk
        }
        
        # Calculate overall risk
        overall_risk = sum(score * self.weights[category] 
                         for category, score in risk_scores.items()
                         if category in self.weights)
        
        risk_scores['overall'] = min(overall_risk * 1.2, 1.0)  # Apply slight uplift but cap at 1.0
        return risk_scores
    
    def get_risk_category(self, risk_score: float) -> str:
        """Categorize risk score into levels"""
        if risk_score < 0.3:
            return 'Low'
        elif risk_score < 0.6:
            return 'Medium'
        else:
            return 'High'
    
    def get_risk_recommendations(self, risk_scores: Dict[str, float], data: Dict) -> List[str]:
        """Generate recommendations based on risk scores and raw data"""
        recommendations = []
        
        # Weather and disaster recommendations
        if risk_scores['weather'] > 0.7:
            if data.get('weather', {}).get('alerts'):
                recommendations.append(f"Urgent: Active weather alerts in the area. Consider immediate "
                                    f"alternative transportation routes and backup suppliers.")
            else:
                recommendations.append("Consider alternative transportation routes and backup suppliers "
                                    "due to adverse weather conditions.")
        
        # Political recommendations
        if risk_scores['political'] > 0.6:
            recommendations.append("High political risk detected. Diversify supplier base across "
                                "different regions and monitor trade policies.")
        
        # Economic recommendations
        if risk_scores['economic'] > 0.6:
            if data.get('trade', {}).get('logistics', 0) < 2.5:
                recommendations.append("Poor logistics performance index detected. Review and optimize "
                                    "supply chain network.")
            recommendations.append("Review and adjust pricing strategies and contract terms due to "
                                "economic risks.")
        
        # Supply recommendations
        if risk_scores['supply'] > 0.5:
            recommendations.append("Increase safety stock levels and identify backup suppliers to "
                                "mitigate supply risks.")
        
        # Demand recommendations
        if risk_scores['demand'] > 0.5:
            recommendations.append("Improve demand forecasting accuracy and implement buffer stock "
                                "strategies.")
        
        # News-based recommendations
        if risk_scores['news_sentiment'] > 0.7:
            recommendations.append("Critical news events detected. Review and update contingency plans.")
        
        return recommendations

    def analyze_supplier(self, supplier_data: Dict) -> Dict:
        """Analyze supplier risk and provide detailed assessment"""
        risk_scores = self.calculate_overall_risk(supplier_data)
        risk_category = self.get_risk_category(risk_scores['overall'])
        recommendations = self.get_risk_recommendations(risk_scores, supplier_data)
        
        return {
            'risk_scores': risk_scores,
            'risk_category': risk_category,
            'recommendations': recommendations,
            'timestamp': pd.Timestamp.now(),
            'raw_data': supplier_data  # Store raw data for reference
        } 