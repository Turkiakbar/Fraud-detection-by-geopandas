# Fraud-detection-by-geopandas
During Week 3 of the Tuwaiq Academy Data and AI Bootcamp, we developed a Python-based project leveraging geospatial datasets to track fraud incidents and analyze their distribution across the United States.

🗺️Fraud Detection by GeoPandas

🚀 Week 3 project from the Tuwaiq Academy Data & AI Bootcamp.
We used Python + GeoPandas with geospatial datasets to detect and visualize fraud incidents across the United States.

✨ Features

 - 🐍 Python + GeoPandas

 - 🌍 Analyze geospatial data of transactions

 - 📊 Visualize fraud distribution by state/region

 - 📂 Interactive dashboard for quick insights

📁 Project Files
File	Description
 - Main_code.ipynb	📝 Exploratory notebook and maps
 - transactions_dashboard.py	🖥️ Script to generate visuals and dashboards
 - df_clean.csv	📄 Cleaned dataset used in the project
⚙️ Installation

Clone the Repository:

 - git clone https://github.com/Turkiakbar/Fraud-detection-by-geopandas.git
 - cd Fraud-detection-by-geopandas


Set Up Environment (Conda recommended):

 - conda create -n fraudgeo python=3.11 -y
 - conda activate fraudgeo
 - conda install -c conda-forge geopandas -y


Or Using Pip:

 - python -m venv .venv
 - .\.venv\Scripts\activate   # Windows
 - pip install geopandas pandas matplotlib

▶️ Usage

 - Run Notebook (EDA & Maps):

 - jupyter notebook Main_code.ipynb


Run Script:

python transactions_dashboard.py

📝 Requirements

 - Python 3.10+

 - GeoPandas

 - Pandas

 - Matplotlib

💡 Notes

 - Make sure df_clean.csv includes location data.

Install GeoPandas in the same environment you’re using to avoid errors.
