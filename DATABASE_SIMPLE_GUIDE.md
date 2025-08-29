# 🗄️ Configuración Simple de Base de Datos

## 📋 Objetivo
- **Local**: Usar Supabase en lugar de SQLite
- **Producción**: Usar Supabase (separado del local)
- **Deploy**: NO tocar nada, mantener como está

## 🏗️ Paso 1: Crear Proyectos en Supabase

### 1.1 Proyecto de Desarrollo (Local)
1. Ve a [supabase.com](https://supabase.com)
2. Crea un proyecto: `runraids-dev`
3. Anota la contraseña que elijas

### 1.2 Proyecto de Producción
1. Crea otro proyecto: `runraids-prod`
2. Anota la contraseña (diferente a la de desarrollo)

## 🔧 Paso 2: Obtener URLs de Conexión

Para cada proyecto:
1. Ve a **Settings** > **Database**
2. Busca la sección **Connection pooling**
3. Copia la **Connection string** completa:
   ```
   postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```

## ⚙️ Paso 3: Configuración Local

### 3.1 Crear archivo .env
Crea un archivo `.env` en la raíz del proyecto:

```env
# Django Configuration
SECRET_KEY=tu-clave-secreta-local
DEBUG=True

# Database - Supabase Development
DATABASE_URL=postgresql://postgres.tu-ref-dev:tu-password-dev@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

### 3.2 Probar la conexión
```bash
# Verificar que conecta a Supabase
python manage.py check_database

# Debería mostrar: "Using PostgreSQL database: aws-0-us-east-1.pooler.supabase.com"
```

### 3.3 Aplicar migraciones
```bash
python manage.py migrate
```

### 3.4 Cargar datos iniciales
```bash
python manage.py load_initial_data
```

### 3.5 Verificar que funciona
```bash
python manage.py runserver
# Ve a http://localhost:8000/admin/ (admin/admin)
```

## 🚀 Paso 4: Configuración de Producción

### 4.1 Variables de Entorno en Vercel
En tu proyecto de Vercel > Settings > Environment Variables:

```
SECRET_KEY=tu-clave-secreta-produccion-diferente
DEBUG=False
DATABASE_URL=postgresql://postgres.tu-ref-prod:tu-password-prod@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

### 4.2 Deploy (sin cambios)
```bash
git add .
git commit -m "Configure Supabase databases"
git push origin main
```

### 4.3 Aplicar migraciones en producción (manual)
Después del deploy, ejecuta una vez:
```bash
# Desde tu terminal local, conectado a la BD de producción
# Cambia temporalmente tu .env para apuntar a producción
DATABASE_URL=postgresql://postgres.tu-ref-prod:tu-password-prod@aws-0-us-east-1.pooler.supabase.com:6543/postgres

python manage.py migrate
python manage.py load_initial_data

# Luego vuelve a cambiar tu .env a desarrollo
```

## 🔍 Comandos de Verificación

### Verificar qué base de datos usa
```bash
python manage.py check_database
```

### Verificar usuarios creados
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.all()
>>> from core.models import Member
>>> Member.objects.all()
```

### Si hay problemas con datos duplicados
```bash
# Limpiar y recargar
python manage.py load_initial_data --clear
```

## 👤 Usuarios Disponibles

### Django Admin
- **Usuario**: `admin`
- **Contraseña**: `admin`
- **URL**: `/admin/`

### Usuarios del Juego
- **Test Member**: `555000001` / `test123`
- **Test Player 1**: `123456789` / `testpass123`
- **Test Player 2**: `987654321` / `testpass123`
- **Admin Player**: `111111111` / `adminpass123`

## 🚨 Troubleshooting

### "Database connection failed"
1. Verifica tu `DATABASE_URL` en `.env`
2. Asegúrate de que el proyecto Supabase esté activo
3. Verifica que la contraseña sea correcta

### "UNIQUE constraint failed"
```bash
python manage.py load_initial_data --clear
```

### "relation does not exist"
```bash
python manage.py migrate
```

### Local sigue usando SQLite
- Verifica que tu archivo `.env` existe
- Verifica que `DATABASE_URL` esté correctamente configurada
- Reinicia el servidor: `python manage.py runserver`

## 📝 Estructura Final

```
Desarrollo Local:
├── .env (DATABASE_URL → Supabase Dev)
├── Aplicación Django
└── Supabase Proyecto Dev

Producción:
├── Vercel (DATABASE_URL → Supabase Prod)
├── Aplicación Django
└── Supabase Proyecto Prod
```

## 🎯 Resumen

1. **Crea 2 proyectos Supabase** (dev y prod)
2. **Configura .env local** con URL de desarrollo
3. **Ejecuta migraciones y datos** en local
4. **Configura variables Vercel** con URL de producción
5. **Deploy normal** (sin cambios en código)
6. **Ejecuta migraciones** en producción una vez

---

¡Ahora tienes Supabase en local y producción sin tocar el deploy! 🎮⚔️
