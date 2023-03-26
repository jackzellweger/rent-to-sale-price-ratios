#!/bin/sh

# Install SQLite
sudo apt-get install -y sqlite3

# Create directory for the SQLite database
# sudo mkdir -p /opt/rent-to-sale-price-ratios/data/db

# Install Python 3, pip, and venv
sudo apt-get install -y python3 python3-pip python3-venv

# Install Jupyter
pip3 install jupyter

# Create virtual environment
python3 -m venv myenv

# Activate virtual environment
source myenv/bin/activate

# Install required python libraries
pip install pandas geopandas pathlib folium branca json os

# Create requirements.txt file
pip freeze > requirements.txt

echo "Packages and dependencies have been installed."

echo "Downloading data & building map..."

sh ./opt/rent-to-sale-price-ratios/build_map.py