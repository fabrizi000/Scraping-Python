#!/bin/bash

sudo apt update
sudo apt upgrade -y

sudo apt install -y \
  wget \
  unzip \
  ca-certificates \
  python3 \
  python3-venv \
  python3-pip \
  python3-tk \
  libgtk-3-0 \
  libnss3 \
  libxss1 \
  libasound2

wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb

wget https://github.com/mozilla/geckodriver/releases/latest/download/geckodriver-linux64.tar.gz
tar -xzf geckodriver-linux64.tar.gz
sudo mv -f geckodriver /usr/local/bin/geckodriver
sudo chmod +x /usr/local/bin/geckodriver

wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
wget https://chromedriver.storage.googleapis.com/$(cat LATEST_RELEASE)/chromedriver_linux64.zip
unzip -o chromedriver_linux64.zip
sudo mv -f chromedriver /usr/local/bin/chromedriver
sudo chmod +x /usr/local/bin/chromedriver

sudo mkdir -p /opt/WebBuster
sudo mkdir -p /opt/WebBuster/scrapers

sudo mv WebBuster /opt/WebBuster/WebBuster
sudo chmod +x /opt/WebBuster/WebBuster

sudo cp -r scrapers/* /opt/WebBuster/scrapers/
sudo cp icono.png /opt/WebBuster/icono.png

DOCS_DIR=$(xdg-user-dir DOCUMENTS)

mkdir -p "$DOCS_DIR/WebBusterResultados/InvestingEconomicCalendar"
mkdir -p "$DOCS_DIR/WebBusterResultados/Elpais"
mkdir -p "$DOCS_DIR/WebBusterResultados/Expansion"
mkdir -p "$DOCS_DIR/WebBusterResultados/Vozpopuli"
mkdir -p "$DOCS_DIR/WebBusterResultados/DatosMacro"

mkdir -p ~/.local/share/applications

cat > ~/.local/share/applications/webbuster.desktop << 'EOF'
[Desktop Entry]
Name=WebBuster
Exec=/opt/WebBuster/WebBuster
Icon=/opt/WebBuster/assets/icono.png
Type=Application
Terminal=false
Categories=Utility;
EOF

chmod +x ~/.local/share/applications/webbuster.desktop
