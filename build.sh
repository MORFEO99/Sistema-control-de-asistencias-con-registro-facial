#!/usr/bin/env bash
# Salir si algún comando falla
set -o errexit

echo "Instalando dependencias del sistema necesarias para dlib/face_recognition..."
apt-get update && apt-get install -y cmake libopenblas-dev liblapack-dev libx11-dev

echo "Instalando paquetes Python..."
pip install -r requirements.txt

echo "Ejecutando migraciones..."
python manage.py migrate

echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "Build completado!"