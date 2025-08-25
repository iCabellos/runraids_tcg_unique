#!/bin/bash
set -euo pipefail

echo "Building RunRaids for Vercel..."

export PYTHONUNBUFFERED=1
export PIP_DISABLE_PIP_VERSION_CHECK=1
export PIP_NO_INPUT=1

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

# --- Verificación de base de datos para evitar sqlite3 en Vercel ---
if [ "${VERCEL:-}" = "1" ] || [ "${VERCEL:-}" = "true" ]; then
  if [ -z "${DATABASE_URL:-}" ]; then
    echo "ERROR: En Vercel se requiere DATABASE_URL (Postgres)."
    echo "Configura la variable de entorno DATABASE_URL en tu proyecto antes del build."
    exit 1
  fi
fi

# --- DEBUG: ver env y engine de Django ---
echo "DEBUG Vercel: VERCEL=${VERCEL:-<no set>}"
if [ -z "${DATABASE_URL:-}" ]; then
  echo "DEBUG: DATABASE_URL está VACÍO en el entorno de build"
else
  echo "DEBUG: DATABASE_URL está DEFINIDO (oculto)"
fi

# Usa el módulo de settings REAL de tu proyecto
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-api.settings}

$PY - <<'PYCODE'
import os, django
print("DEBUG: DJANGO_SETTINGS_MODULE =", os.getenv("DJANGO_SETTINGS_MODULE"))
try:
    django.setup()
    from django.conf import settings
    print("DEBUG: ENGINE =", settings.DATABASES['default']['ENGINE'])
    print("DEBUG: NAME   =", settings.DATABASES['default'].get('NAME'))
except Exception as e:
    print("DEBUG: django.setup() error ->", repr(e))
PYCODE

# --- Collect static ---
$PY manage.py collectstatic --noinput --clear

# --- Collect static ---
# NOTA: no ejecutamos migraciones ni seeds en el paso de build de Vercel.
$PY manage.py collectstatic --noinput --clear

# --- Preparar carpeta de salida para Vercel ---
OUT_DIR="staticfiles_build"
mkdir -p "$OUT_DIR"

# Copiar estáticos desde ubicaciones comunes a la carpeta de salida
COPIED=false
for CANDIDATE in "staticfiles" "static" "assets"; do
  if [ -d "$CANDIDATE" ]; then
    echo "Copiando estáticos desde '$CANDIDATE' a '$OUT_DIR'..."
    cp -R "$CANDIDATE"/. "$OUT_DIR"/ || true
    COPIED=true
  fi
done

# Placeholder si no se encontró nada (para que Vercel detecte la carpeta)
if [ "$COPIED" = false ]; then
  echo "ADVERTENCIA: No se encontró carpeta de estáticos conocida. Creando placeholder en '$OUT_DIR'."
  echo "{}" > "$OUT_DIR/vercel_placeholder.json"
fi

echo "Build completed successfully!"
