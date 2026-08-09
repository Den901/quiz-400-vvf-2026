#!/bin/sh
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then
  python3 portable_server.py
else
  echo "Python 3 non è installato ed è necessario per Quiz 400 VVF 2026."
  printf "Vuoi scaricarlo e installarlo ora dal sito ufficiale? [s/N] "
  read -r answer
  case "$answer" in
    s|S|si|SI|sì|SÌ)
      pkg="${TMPDIR:-/tmp}/python-3.14.7-macos11.pkg"
      echo "Scaricamento dell'installer ufficiale Python..."
      curl --fail --location "https://www.python.org/ftp/python/3.14.7/python-3.14.7-macos11.pkg" --output "$pkg" || exit 1
      echo "macOS chiederà la password di amministratore per completare l'installazione."
      sudo /usr/sbin/installer -pkg "$pkg" -target / || exit 1
      rm -f "$pkg"
      /usr/local/bin/python3 portable_server.py
      ;;
    *) echo "Installazione annullata." ;;
  esac
fi
