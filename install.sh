#!/bin/bash
set -e

echo "Instalace sccli..."

INSTALL_DIR="$HOME/.local/share/sccli"

mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

git clone https://github.com/kralicekgamer/sccli repo
cd repo

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

echo "source $INSTALL_DIR/repo/.venv/bin/activate && python3 $INSTALL_DIR/repo/sccli.py \"\$@\"" > sccli
chmod +x sccli

mkdir -p "$HOME/.local/bin"
mv sccli "$HOME/.local/bin/sccli"

echo "Instalace dokončena."
