# Supply Chain Risk Monitoring System (SCRMS)

A machine learning-based system for analyzing and monitoring supply chain risks across global suppliers.

## Features

- Real-time risk scoring using ML algorithms
- Interactive geospatial mapping
- Multi-factor risk analysis (location, weather, economics)
- Real-time analytics dashboard
- Supplier risk assessment
- Alert system for supply chain disruptions

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/supplychain-analyzer.git
cd supplychain-analyzer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file with:
```
NEWS_API_KEY=your_news_api_key
WEATHER_API_KEY=your_weather_api_key
```

5. Run the application:
```bash
streamlit run streamlit_app.py
```

## Project Structure

- `src/`: Source code for the application
  - `data_collection/`: Data ingestion and API collectors
  - `models/`: ML models for risk scoring and prediction
  - `database/`: Database operations and schemas
  - `visualization/`: Dashboard and visualization components
- `config/`: Configuration files
- `data/`: Data storage
- `tests/`: Unit tests

## Usage

1. Access the dashboard at `http://localhost:8501`
2. Upload supplier data or connect to data sources
3. View real-time risk assessments and analytics
4. Configure alert thresholds and monitoring parameters

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request