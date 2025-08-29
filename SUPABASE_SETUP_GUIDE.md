# 🗄️ Configuración Supabase para Local y Producción

## 📋 Nuevo Flujo de Trabajo

- **Local**: Supabase (base de datos de desarrollo)
- **Producción**: Supabase (base de datos de producción)
- **Build automático**: Migraciones y datos iniciales se aplican automáticamente

## 🏗️ Paso 1: Crear Proyectos en Supabase

### 1.1 Proyecto de Desarrollo
1. Ve a [supabase.com](https://supabase.com)
2. Crea un proyecto: `runraids-dev`
3. Guarda la contraseña de la base de datos

### 1.2 Proyecto de Producción
1. Crea otro proyecto: `runraids-prod`
2. Guarda la contraseña (diferente a desarrollo)

## 🔧 Paso 2: Obtener URLs de Conexión

### Para cada proyecto:
1. Ve a **Settings** > **Database**
2. Busca **Connection pooling**
3. Copia la **Connection string**:
   ```
   postgresql://postgres.xxxxx:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```

## ⚙️ Paso 3: Configuración Local

### 3.1 Crear archivo .env
```env
# Django Configuration
SECRET_KEY=tu-clave-secreta-local
DEBUG=True

# Database - Supabase Development
DATABASE_URL=postgresql://postgres.dev-ref:dev-password@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

### 3.2 Setup inicial
```bash
# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py migrate

# Cargar datos iniciales
python manage.py load_initial_data

# Verificar
python manage.py check_database

# Ejecutar servidor
python manage.py runserver
```

## 🚀 Paso 4: Configuración en Vercel

### 4.1 Variables de Entorno
En Vercel Dashboard > Settings > Environment Variables:

```
SECRET_KEY=tu-clave-secreta-produccion-diferente
DEBUG=False
DATABASE_URL=postgresql://postgres.prod-ref:prod-password@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

### 4.2 Deploy
```bash
git add .
git commit -m "Configure Supabase for local and production"
git push origin main
```

## ✨ Paso 5: Verificación Automática

### En Vercel (automático):
1. **Build detecta Supabase**: Conecta automáticamente
2. **Aplica migraciones**: `python manage.py migrate`
3. **Carga datos**: `python manage.py load_initial_data`
4. **Deploy completo**: Aplicación lista

### Verificar funcionamiento:
- Ve a tu URL de Vercel
- Accede a `/admin/` con `admin/admin`
- Verifica que el juego funciona

## 🔍 Comandos de Verificación

### Local
```bash
# Verificar conexión
python manage.py check_database

# Ver qué base de datos usa
python manage.py shell
>>> from django.db import connection
>>> print(connection.settings_dict)

# Verificar usuarios
>>> from django.contrib.auth.models import User
>>> User.objects.all()
```

### Producción
- Revisa logs en Vercel Dashboard
- Accede al admin panel
- Verifica que los datos están cargados

## 🛠️ Comandos Útiles

### Gestión de Datos
```bash
# Cargar datos (respeta existentes)
python manage.py load_initial_data

# Limpiar y recargar
python manage.py load_initial_data --clear

# Reset completo
python manage.py reset_database --confirm
```

### Gestión de Migraciones
```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Ver estado
python manage.py showmigrations
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
3. Verifica la contraseña

### "Build failed on Vercel"
1. Revisa los logs en Vercel Dashboard
2. Verifica las variables de entorno
3. Asegúrate de que `DATABASE_URL` esté configurada

### "relation does not exist"
```bash
python manage.py migrate
```

### Los datos no se cargan
```bash
python manage.py load_initial_data --verbosity=2
```

## 📝 Ventajas del Nuevo Flujo

✅ **Consistencia**: Misma base de datos (PostgreSQL) en local y producción
✅ **Automático**: Build de Vercel aplica migraciones y carga datos
✅ **Separación**: Bases de datos completamente separadas para dev/prod
✅ **Escalable**: Supabase maneja el crecimiento automáticamente
✅ **Backup**: Supabase hace backups automáticos

## 🎯 Próximos Pasos

1. **Configura Supabase** siguiendo los pasos de arriba
2. **Crea tu `.env`** con la URL de desarrollo
3. **Ejecuta setup local**: `python manage.py migrate && python manage.py load_initial_data`
4. **Configura Vercel** con la URL de producción
5. **Deploy**: `git push origin main`

---

¡Tu aplicación ahora usa Supabase en todos los entornos! 🎮⚔️
