#!/bin/bash
set -e

echo "Odinstalace sccli..."

BIN="$HOME/.local/bin/sccli"
INSTALL_DIR="$HOME/.local/share/sccli"

# 1) Smazat binárku
if [ -f "$BIN" ]; then
    echo "Mazání $BIN"
    rm "$BIN"
else
    echo "Binárka sccli nebyla nalezena v ~/.local/bin"
fi

if [ -d "$INSTALL_DIR" ]; then
    echo "Mazání adresáře $INSTALL_DIR"
    rm -rf "$INSTALL_DIR"
else
    echo "Instalační adresář nebyl nalezen"
fi

echo "Odinstalace dokončena."
