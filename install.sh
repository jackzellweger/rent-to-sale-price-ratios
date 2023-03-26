#!/bin/bash

# ----- IN README FOR USER TO RUN -----

# `sudo apt-get update; sudo apt-get install -y git`

# `cd /root/..`

# `mkdir ./opt; mkdir ./opt/real_estate_project`

# `git clone https://github.com/jackzellweger/rent-to-sale-price-ratios.git ./opt/real_estate_project`

# ----- END IN README FOR USER TO RUN -----

cd /root/../opt/real_estate_project

# Bring package lists up to date
sudo apt-get update

# Install SQLite
sudo apt-get install -y sqlite3

# Create directory for the SQLite database
# sudo mkdir -p /opt/rent-to-sale-price-ratios/data/db

# Install Python 3, pip, and venv
sudo apt-get install -y python3 python3-pip python3-venv

# Install unzip package
sudo apt-get install unzip

# Install Jupyter
pip3 install jupyter

# Create virtual environment
python3 -m venv myenv

# Activate virtual environment
source myenv/bin/activate

# Install required python libraries
pip install pandas geopandas pathlib folium branca

# Create requirements.txt file
pip freeze > requirements.txt

echo "Packages and dependencies have been installed."

echo "Downloading data & building map..."

chmod u+x build_map.sh

./build_map.sh
