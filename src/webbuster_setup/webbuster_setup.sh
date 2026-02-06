#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "Este instalador debe ejecutarse con sudo"
  exit 1
fi

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Actualizando sistema"
apt update
apt upgrade -y

echo "Instalando dependencias del sistema"
apt install -y \
  python3 \
  python3-venv \
  python3-tk \
  wget \
  curl \
  unzip \
  ca-certificates \
  gnupg \
  libglib2.0-0 \
  libgl1

echo "Instalando Firefox"
apt install -y firefox-esr

echo "Descargando geckodriver"
GECKO_VERSION="v0.36.0"
GECKO_URL="https://github.com/mozilla/geckodriver/releases/download/${GECKO_VERSION}/geckodriver-${GECKO_VERSION}-linux64.tar.gz"
wget -O /tmp/geckodriver.tar.gz "$GECKO_URL"
tar -xzf /tmp/geckodriver.tar.gz -C /tmp
mv /tmp/geckodriver /usr/bin/geckodriver
chmod +x /usr/bin/geckodriver

echo "Instalando Google Chrome"
if ! command -v google-chrome >/dev/null 2>&1; then
  wget -O /tmp/google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  dpkg -i /tmp/google-chrome.deb || apt -f install -y
fi

echo "Actualizando Google Chrome"
apt upgrade -y google-chrome-stable || true

echo "Detectando version de Google Chrome"
CHROME_VERSION=$(google-chrome --version | grep -oP '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')
CHROME_MAJOR=$(echo "$CHROME_VERSION" | cut -d. -f1)

echo "Descargando chromedriver compatible"
CHROMEDRIVER_URL=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json \
  | python3 -c "
import json,sys
data=json.load(sys.stdin)
major='$CHROME_MAJOR'
for v in data['versions']:
    if v['version'].startswith(major + '.'):
        for d in v['downloads']['chromedriver']:
            if d['platform'] == 'linux64':
                print(d['url'])
                sys.exit(0)
sys.exit(1)
" || true)

if [ -n "$CHROMEDRIVER_URL" ]; then
  wget -O /tmp/chromedriver.zip "$CHROMEDRIVER_URL"
  unzip -o /tmp/chromedriver.zip -d /tmp
  mv /tmp/chromedriver-linux64/chromedriver /usr/bin/chromedriver
  chmod +x /usr/bin/chromedriver
else
  echo "No se pudo determinar chromedriver compatible. Se omite este paso."
fi

echo "Creando estructura en /opt"
mkdir -p /opt/WebBuster/scrapers

echo "Copiando WebBuster y scrapers"
cp -f "$BASE_DIR/WebBuster" /opt/WebBuster/WebBuster
cp -f "$BASE_DIR/icono.png" /opt/WebBuster/icono.png
cp -rf "$BASE_DIR/scrapers/"* /opt/WebBuster/scrapers/
chmod +x /opt/WebBuster/WebBuster

echo "Creando entorno virtual de Python"
python3 -m venv /opt/WebBuster/venv

echo "Instalando dependencias de Python en el entorno virtual"
source /opt/WebBuster/venv/bin/activate
pip install --upgrade pip
pip install selenium pandas requests beautifulsoup4 lxml matplotlib numpy
deactivate

echo "Creando estructura de carpetas en Documentos/Documents para cada usuario"
for dir in /home/*; do
  if [ -d "$dir" ]; then
    DOCS="$dir/Documents"
    [ -d "$DOCS" ] || DOCS="$dir/Documentos"

    if [ -d "$DOCS" ]; then
      mkdir -p "$DOCS/WebBusterResultados/InvestingEconomicCalendar"
      mkdir -p "$DOCS/WebBusterResultados/DatosMacro"
      mkdir -p "$DOCS/WebBusterResultados/Elpais"
      mkdir -p "$DOCS/WebBusterResultados/Expansion"
      mkdir -p "$DOCS/WebBusterResultados/Vozpopuli"
      chown -R "$(basename "$dir")":"$(basename "$dir")" "$DOCS/WebBusterResultados"
    fi
  fi
done

echo "Creando acceso directo"
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

echo "Instalacion completada"
