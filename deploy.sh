#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="/home/julian/aplicaciones/Patitas-Vet"
VENV_DIR="/home/julian/aplicaciones/venv"
GUNICORN_SERVICE="gunicorn"
NGINX_SERVICE="nginx"

echo "==> Entrando al proyecto"
cd "$PROJECT_DIR"

echo "==> Actualizando código desde Git"
git pull

echo "==> Activando entorno virtual"
source "$VENV_DIR/bin/activate"

echo "==> Instalando dependencias"
pip install -r requirements.txt

echo "==> Aplicando migraciones"
python manage.py migrate

echo "==> Recolectando archivos estáticos"
python manage.py collectstatic --noinput

echo "==> Verificando configuración de Django"
python manage.py check

echo "==> Reiniciando Gunicorn"
sudo systemctl restart "$GUNICORN_SERVICE"

echo "==> Verificando Nginx"
sudo nginx -t

echo "==> Reiniciando Nginx"
sudo systemctl restart "$NGINX_SERVICE"

echo "==> Estado de servicios"
sudo systemctl --no-pager --full status "$GUNICORN_SERVICE" | head -n 20
sudo systemctl --no-pager --full status "$NGINX_SERVICE" | head -n 20

echo "==> Deploy finalizado correctamente"
