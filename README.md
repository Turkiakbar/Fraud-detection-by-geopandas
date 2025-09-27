# Fraud-detection-by-geopandas
During Week 3 of the Tuwaiq Academy Data and AI Bootcamp, we developed a Python-based project leveraging geospatial datasets to track fraud incidents and analyze their distribution across the United States.

Fraud Detection by GeoPandas

During Week 3 of the Tuwaiq Academy Data & AI Bootcamp, we built a Python project that uses GeoPandas to visualize and analyze the geographic distribution of suspected fraud incidents across the United States. 
GitHub

Repository structure

Main_code.ipynb — exploratory notebook and maps

transactions_dashboard.py — script for generating visuals/summary

df_clean.csv — cleaned dataset used in the project 
GitHub

Quick start
1) Clone
git clone https://github.com/Turkiakbar/Fraud-detection-by-geopandas.git
cd Fraud-detection-by-geopandas

2) Create environment & install deps

Tip (Windows): using conda-forge is the easiest way to get GeoPandas and its native deps (PROJ, GEOS, GDAL).

Using conda:

conda create -n fraudgeo python=3.11 -y
conda activate fraudgeo
conda install -c conda-forge geopandas -y


Using pip (works best inside a virtualenv):

python -m venv .venv
.\.venv\Scripts\activate          # on Windows (PowerShell)
# source .venv/bin/activate       # on macOS/Linux
pip install geopandas pandas matplotlib


If pip shows errors, install the base libs explicitly:

pip install shapely pyproj fiona rtree

3) Run

Notebook (EDA & maps):

jupyter notebook Main_code.ipynb


Script:

python transactions_dashboard.py

What it does

Loads cleaned transactions data (df_clean.csv)

Converts location fields to geospatial data

Maps & summarizes fraud distribution by state/region

Produces basic charts/tables to support exploration

Requirements

Python 3.10+

GeoPandas, Pandas, (Matplotlib optional)

Notes

Data in df_clean.csv should include columns for location (e.g., state or lat/long) and a fraud indicator.

If you run into ModuleNotFoundError: geopandas, install it in the same environment you’re using to run the code (see steps above).
