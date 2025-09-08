#!/bin/bash

# Wrapper zur Installation des lokalen .deb Pakets inklusive automatischer Auflösung der Abhängigkeiten.
# Nutzung: sudo ./scripts/install-deb.sh pi-usb-safegate_1.0.1_all.deb

set -euo pipefail

if [[ $(id -u) -ne 0 ]]; then
    echo "Dieses Skript muss mit sudo/root ausgeführt werden." >&2
    exit 1
fi

if [[ $# -lt 1 ]]; then
    echo "Verwendung: sudo $0 <paketdatei.deb>" >&2
    exit 1
fi

PKG_FILE="$1"

if [[ ! -f "$PKG_FILE" ]]; then
    echo "Datei nicht gefunden: $PKG_FILE" >&2
    exit 1
fi

echo "Aktualisiere Paketlisten..."
apt-get update -qq

echo "Installiere Paket mit automatischer Auflösung der Abhängigkeiten..."
apt-get install -y "./$PKG_FILE"

echo "Fertig. Prüfe Status:"
dpkg -s pi-usb-safegate | grep -E 'Status|Version' || true

echo "Nächste Schritte:"
echo "  sudo pi-usb-safegate-setup   # Ersteinrichtung"
echo "  sudo pi-usb-safegate         # Start"
