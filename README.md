# 🏃 Personal Health Analytics Dashboard

An end-to-end data science project exploring **9 years of personal Apple Health data (1.1M+ records)**.  
The project builds a full pipeline from Apple Health XML exports to an interactive dashboard, with an AI health assistant that can answer questions based on the data.

🔗 **Live Demo:**  
https://apple-health-analytics-vknian.streamlit.app

---

# 📊 Project Overview

Apple Health exports data in XML format, which makes it difficult to explore directly.  
This project parses and processes those exports into structured datasets and builds a dashboard to analyze long-term trends in activity, sleep, and heart rate.

The goal was to turn raw personal health logs into something that is actually interpretable and useful.

---

# 🔍 Features

### Activity Analysis
- Daily step trends across 9 years
- 30-day rolling averages to visualize long-term patterns

### Sleep Analysis
- Sleep duration trends
- Distribution and weekday/weekend comparison

### Heart Rate Analysis
- Resting heart rate trends over time
- Relationship between heart rate and daily activity

### Correlation Analysis
- Quantifies how sleep duration affects next-day activity (**r = 0.29**)

### Anomaly Detection
- Isolation Forest model to detect unusual health days

### AI Health Assistant
- Claude-powered agent that can answer questions about the dataset

---

# 🛠️ Tech Stack

| Layer | Tools |
|------|------|
| Data Processing | Python, XML parsing, pandas |
| Analysis | numpy, scipy, scikit-learn |
| Visualization | plotly, matplotlib |
| Dashboard | Streamlit |
| AI Integration | Anthropic Claude API |
| Data Source | Apple Health export |

---

# 📈 Key Findings

- Processed **1.1M+ health records** from **2017–2026**
- Sleep duration improved from **~5.5 hrs (2018)** to **~8 hrs (2023+)**
- Peak activity year was **2023** with **12,223 average steps/day**
- Sleep shows a moderate positive correlation with next-day activity (**r = 0.29**)
- Anomaly detection flagged unusual health days using **Isolation Forest**
- Step counts are consistently higher on weekdays than weekends

---

## 🗂️ Project Structure
```
apple-health-analytics/
├── dashboard/
│   └── app.py          # Streamlit dashboard + AI agent
├── notebooks/
│   └── Health_analysis.ipynb  # EDA & analysis notebook
├── scripts/
│   └── parse_health.py # XML → CSV parser
└── requirements.txt
```

## 🚀 Run Locally
```bash
git clone https://github.com/victorianian610/apple-health-analytics
cd apple-health-analytics
pip install -r requirements.txt

# Add your API key
echo "ANTHROPIC_API_KEY=your-key" > .env

# Export Apple Health data from iPhone:
# Health App → Profile → Export All Health Data → save export.xml to data/
python scripts/parse_health.py

streamlit run dashboard/app.py
```

## 💡 Product Insights

This project raises key product questions relevant to health tech:
- What caused the 2023 activity peak? How can a health app replicate that trigger?
- Sleep is the "root metric" — improving sleep drives all other health improvements
- Anomaly detection can power real-time health alerts and premium features
- Personalized AI coaching bridges the gap between raw data and actionable advice
