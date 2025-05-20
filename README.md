# 📊 Exoplanet Explorer Dashboard Plan

This project is a simple and interactive data visualization app built using **Streamlit**, **Pandas**, **NumPy** and **Plotly**.

## 🚀 Features

- Interactive web UI with **Streamlit**
- Efficient data handling using **Pandas** and **NumPy**
- Visualization using **Plotly** for interactive charts

## 📁 Project Structure

```

Exoplanet-Explorer-Dashboard-Plan/
├── .gitignore               \# Specifies intentionally untracked files that Git should ignore
├── Dashboard.py                   \# Main Streamlit app script
├── data/
│   └── exoplanets\_full\_features.csv \# Dataset for the application
├── pages/
│   ├── 01\_Planetary\_Discovery.py    \# Streamlit page for planetary discovery insights
│   ├── 02\_Habitability\_Factors.py   \# Streamlit page for habitability factors
│   └── 03\_Star\_Planet\_Relationships.py \# Streamlit page for star-planet relationships
├── utils/
│   ├── **init**.py          \# Makes 'utils' a Python package
│   └── data\_loader.py       \# Utility script for loading data
├── venv/                    \# Virtual environment directory
├── README.md                \# Project documentation
└── requirements.txt         \# List of dependencies

````

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone [https://github.com/muhammad-mahad/Exoplanet-Explorer-Dashboard-Plan.git](https://github.com/muhammad-mahad/Exoplanet-Explorer-Dashboard-Plan.git)
cd Exoplanet-Explorer-Dashboard-Plan
````

### 2\. Create and Activate a Virtual Environment

#### On Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### On Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3\. Install Required Packages

```bash
pip install -r requirements.txt
```

### 4\. Run the Streamlit App

Replace `Dashboard.py` with the name of your script:

```bash
streamlit run Dashboard.py
```

## ✅ Requirements

See [`requirements.txt`](https://www.google.com/search?q=./requirements.txt) for the list of required packages.

To regenerate it after adding new packages:

```bash
pip freeze > requirements.txt
```