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

DESKTOP_FILE="/usr/share/applications/webbuster.desktop"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=WebBuster
Comment=Herramienta de scraping economico
Exec=/opt/WebBuster/WebBuster
Icon=/opt/WebBuster/icono.png
Terminal=false
Categories=Utility;
EOF

chmod 644 "$DESKTOP_FILE"

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

# Crear la carpeta de la aplicación en /opt
sudo mkdir -p /opt/CSVLOADER

# Copiar el ejecutable onefile a /opt/CSVLOADER
sudo cp csvh /opt/CSVLOADER/csvh

# Copiar el icono a /opt/CSVLOADER
sudo cp icono1.png /opt/CSVLOADER/icono1.png

# Dar permisos de ejecución al binario principal
sudo chmod +x /opt/CSVLOADER/csvh

# Crear el acceso directo en el menú de aplicaciones
cat << EOF | sudo tee /usr/share/applications/csvloader.desktop
[Desktop Entry]
Name=CSV LOADER
Exec=/opt/CSVLOADER/csvh
Icon=/opt/CSVLOADER/icono1.png
Type=Application
Categories=Utility;
EOF
