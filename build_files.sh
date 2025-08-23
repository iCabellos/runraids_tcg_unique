#!/bin/bash
set -euo pipefail

echo "Building RunRaids for Vercel..."

# --- Resolver binarios de Python/Pip ---
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "ERROR: Python no está disponible en el entorno de build."
  exit 1
fi

if command -v pip3 >/dev/null 2>&1; then
  PIP=pip3
elif command -v pip >/dev/null 2>&1; then
  PIP=pip
else
  # Intento final: usar -m pip desde Python
  if $PY -m pip --version >/dev/null 2>&1; then
    PIP="$PY -m pip"
  else
    echo "ERROR: pip no está disponible en el entorno de build."
    exit 1
  fi
fi

# --- Virtualenv para aislar dependencias ---
if [ ! -d ".venv" ]; then
  $PY -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
$PIP install --upgrade pip wheel
$PIP install -r requirements.txt

# --- Collect static ---
# NOTA: no ejecutamos migraciones ni seeds en el paso de build de Vercel.
$PY manage.py collectstatic --noinput --clear

# --- Preparar carpeta de salida para Vercel ---
OUT_DIR="staticfiles_build"
mkdir -p "$OUT_DIR"

# Si tu STATIC_ROOT ya deja los archivos en 'staticfiles' (o similar), los copiamos a OUT_DIR.
COPIED=false
for CANDIDATE in "staticfiles" "static" "assets"; do
  if [ -d "$CANDIDATE" ]; then
    echo "Copiando estáticos desde '$CANDIDATE' a '$OUT_DIR'..."
    # Copiamos el contenido preservando estructura
    cp -R "$CANDIDATE"/. "$OUT_DIR"/ || true
    COPIED=true
  fi
done

# En caso extremo, deja al menos un placeholder para que Vercel detecte la carpeta
if [ "$COPIED" = false ]; then
  echo "ADVERTENCIA: No se encontró carpeta de estáticos conocida. Creando placeholder en '$OUT_DIR'."
  echo "{}" > "$OUT_DIR/vercel_placeholder.json"
fi

echo "Build completed successfully!"
