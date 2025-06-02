# 📰 Nova Financial Solutions — Sentiment-Based Price Movement Prediction

[![CI](https://github.com/your-username/financial-news-sentiment/actions/workflows/test.yml/badge.svg)](https://github.com/your-username/financial-news-sentiment/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Made with Python](https://img.shields.io/badge/Made%20with-Python%203.10-blue.svg)](https://www.python.org/)
[![Build with Make](https://img.shields.io/badge/build%20tool-Make-green)](Makefile)

This project analyzes the relationship between **financial news sentiment** and **stock price movements** using natural language processing, time series analysis, and visualization. Built for **10 Academy’s AIM Week 1 Challenge**, it focuses on developing a sentiment analysis pipeline that supports financial decision-making.

---

## 📊 Project Structure

```
.
├── data/                    # Raw, interim, and processed data files
├── notebooks/              # Exploratory analysis and development notebooks
├── src/
│   ├── eda/                # Exploratory Data Analysis utilities
│   │   └── visualizer.py
│   ├── models/             # Modeling components (e.g., topic modeling)
│   └── sentiment_analyzer.py
├── tests/                  # Unit tests for all modules
│   └── data/
│       ├── test_visualizer.py
│       └── test_sentiment_analyzer.py
├── requirements.txt        # Python dependencies
├── Makefile                # Common development tasks
├── README.md               # Project documentation
└── .gitignore              # Ignored files
```

---

## ⚙️ Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/financial-news-sentiment.git
   cd financial-news-sentiment
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run tests**
   ```bash
   make test
   ```

---

## 🧠 Features

### ✅ Sentiment Analysis
- Uses **VADER** to classify headlines into Positive, Neutral, or Negative.
- Annotates each headline with a compound sentiment score and label.

### ✅ Visualizations
- Headline length distribution
- Articles per publisher
- Sentiment distribution over time
- Weekday publishing trends

### ✅ Correlation Analysis
- Compares sentiment trends against closing stock prices to assess correlation.

### ✅ Topic Modeling (optional)
- Topic extraction using NLP techniques for trend analysis (e.g., LDA, BERTopic).

---

## 📈 Example Use

```python
from src.sentiment_analyzer import SentimentAnalyzer
import pandas as pd

df = pd.read_csv("data/raw/financial_headlines.csv")
analyzer = SentimentAnalyzer(text_col="headline")
df_scored = analyzer.apply_to_dataframe(df)
analyzer.plot_sentiment_distribution(df_scored)
```

---

## 📦 Dependencies

- `pandas`
- `matplotlib`
- `seaborn`
- `vaderSentiment`
- `pytest`

Install them all using:
```bash
pip install -r requirements.txt
```

---

## 📄 License

This project is developed as part of a **10 Academy** training challenge. Content may be reused with attribution.

---

## 👨‍💻 Author

**Nova Financial Solutions**
Built with ❤️ by a 10 Academy Trainee
For Week 1 of the AIM Challenge Track — Data Science & Financial Analytics
