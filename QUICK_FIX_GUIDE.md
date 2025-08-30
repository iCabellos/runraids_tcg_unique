# 🔧 Guía Rápida de Solución de Problemas

## 🚨 Error: "UNIQUE constraint failed: core_member.id"

### Causa
Ya existen datos en la base de datos y el comando intenta crear duplicados.

### Soluciones

#### Opción 1: Limpiar y recargar (Recomendado)
```bash
python manage.py load_initial_data --clear
```

#### Opción 2: Reset completo de la base de datos
```bash
python manage.py reset_database --confirm
```

#### Opción 3: Setup automático con manejo de duplicados
```bash
python setup_database.py
# El script detectará datos existentes y preguntará qué hacer
```

## 🗄️ Problemas Comunes de Base de Datos

### "relation does not exist"
```bash
python manage.py migrate
```

### "no such table: core_member"
```bash
python manage.py migrate
python manage.py load_initial_data
```

### "Database connection failed"
1. Verifica tu `.env`:
   ```env
   DATABASE_URL=postgresql://postgres.xxxxx:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```
2. Verifica que Supabase esté activo
3. Verifica la contraseña

### Los datos no se cargan
```bash
# Con más información de debug
python manage.py load_initial_data --verbosity=2

# Forzar recarga
python manage.py load_initial_data --clear
```

## 🎮 Verificar que Todo Funciona

### 1. Verificar conexión de base de datos
```bash
python manage.py check_database
```

### 2. Verificar usuarios creados
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.all()
>>> from core.models import Member
>>> Member.objects.all()
```

### 3. Probar el servidor
```bash
python manage.py runserver
# Ve a http://localhost:8000/admin/ (admin/admin)
```

## 🛠️ Comandos Útiles

### Gestión de Datos
```bash
# Cargar datos iniciales (respeta existentes)
python manage.py load_initial_data

# Limpiar y recargar datos
python manage.py load_initial_data --clear

# Reset completo de la base de datos
python manage.py reset_database --confirm

# Verificar configuración
python manage.py check_database

# Setup automático completo
python setup_database.py
```

### Gestión de Migraciones
```bash
# Aplicar migraciones
python manage.py migrate

# Crear nuevas migraciones
python manage.py makemigrations

# Ver estado de migraciones
python manage.py showmigrations
```

### Gestión de Usuarios
```bash
# Crear superusuario manualmente
python manage.py createsuperuser

# Cambiar contraseña de usuario
python manage.py changepassword admin
```

## 🔄 Flujo de Trabajo Recomendado

### Para Desarrollo Local
1. **Primera vez**:
   ```bash
   python setup_database.py
   ```

2. **Si hay problemas con datos**:
   ```bash
   python manage.py reset_database --confirm
   ```

3. **Para actualizaciones de modelos**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py load_initial_data
   ```

### Para Producción
1. **Variables de entorno en Vercel**:
   - `DATABASE_URL`: URL de Supabase de producción
   - `SECRET_KEY`: Clave segura
   - `DEBUG`: `False`

2. **Deploy**:
   ```bash
   git add .
   git commit -m "Database fixes"
   git push origin main
   ```

## 👤 Usuarios Disponibles Después del Setup

### Django Admin
- **Usuario**: `admin`
- **Contraseña**: `admin`
- **URL**: `/admin/`

### Usuarios del Juego
- **Test Member**: `555000001` / `test123`
- **Test Player 1**: `123456789` / `testpass123`
- **Test Player 2**: `987654321` / `testpass123`
- **Admin Player**: `111111111` / `adminpass123`

## 🆘 Si Nada Funciona

### Reset Completo
```bash
# 1. Borrar base de datos SQLite (si usas local)
rm db.sqlite3

# 2. Reset migraciones (CUIDADO: solo en desarrollo)
rm core/migrations/0*.py

# 3. Crear nuevas migraciones
python manage.py makemigrations core

# 4. Aplicar migraciones
python manage.py migrate

# 5. Cargar datos
python manage.py load_initial_data
```

### Para PostgreSQL/Supabase
```bash
# 1. Conectar a la base de datos
python manage.py dbshell

# 2. Borrar todas las tablas (CUIDADO)
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

# 3. Salir y aplicar migraciones
python manage.py migrate
python manage.py load_initial_data
```

---

¡Con estos comandos deberías poder solucionar cualquier problema! 🎮⚔️
