# 📊 Exoplanet Explorer Dashboard Plan

This project is a simple and interactive data visualization app built using **Streamlit**, **Pandas**, **NumPy**, **Plotly**, **Matplotlib**, and **Seaborn**.

## 🚀 Features

- Interactive web UI with **Streamlit**
- Efficient data handling using **Pandas** and **NumPy**
- Multiple visualization options using:
  - **Plotly** for interactive charts
  - **Matplotlib** and **Seaborn** for static charts

## 📁 Project Structure

```
streamlit-data-viz/
├── app.py             # Main Streamlit app script
├── requirements.txt        # List of dependencies
└── README.md               # Project documentation
```

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/muhammad-mahad/Exoplanet-Explorer-Dashboard-Plan.git
cd Exoplanet-Explorer-Dashboard-Plan
```

### 2. Create and Activate a Virtual Environment

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

### 3. Install Required Packages

```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit App

Replace `app.py` with the name of your script:

```bash
streamlit run app.py
```

## ✅ Requirements

See [`requirements.txt`](./requirements.txt) for the list of required packages.

To regenerate it after adding new packages:

```bash
pip freeze > requirements.txt
```

## 📌 Notes

- Use Python 3.7 or later.
- You can customize the app and add your dataset and visualizations.
- Optionally, create `.streamlit/config.toml` to tweak UI settings like theme.
