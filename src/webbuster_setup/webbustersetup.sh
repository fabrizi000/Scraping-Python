#!/bin/bash

sudo apt update
sudo apt upgrade -y

sudo apt install -y python3 python3-venv python3-tk wget curl unzip ca-certificates gnupg libglib2.0-0 libgl1

# Google Chrome
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb
rm -f google-chrome-stable_current_amd64.deb

# Geckodriver
wget https://github.com/mozilla/geckodriver/releases/download/v0.35.0/geckodriver-v0.35.0-linux64.tar.gz
tar -xzf geckodriver-v0.35.0-linux64.tar.gz
sudo mv -f geckodriver /usr/local/bin/geckodriver
sudo chmod +x /usr/local/bin/geckodriver
rm -f geckodriver-v0.35.0-linux64.tar.gz

# Chromedriver (en tu sistema sale plano, sin carpeta)
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
wget https://chromedriver.storage.googleapis.com/$(cat LATEST_RELEASE)/chromedriver_linux64.zip
unzip -o chromedriver_linux64.zip
sudo mv -f chromedriver /usr/local/bin/chromedriver
sudo chmod +x /usr/local/bin/chromedriver
rm -f chromedriver_linux64.zip LATEST_RELEASE LICENSE.chromedriver

# Estructura en /opt
sudo mkdir -p /opt/WebBuster/scrapers
sudo cp -f WebBuster /opt/WebBuster/WebBuster
sudo cp -f icono.png /opt/WebBuster/icono.png
sudo cp -rf scrapers/* /opt/WebBuster/scrapers/
sudo chmod +x /opt/WebBuster/WebBuster

# Entorno venv
sudo python3 -m venv /opt/WebBuster/venv
source /opt/WebBuster/venv/bin/activate
pip install --upgrade pip
pip install selenium pandas requests beautifulsoup4 lxml matplotlib numpy
deactivate
