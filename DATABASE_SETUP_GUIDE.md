# 🗄️ Guía de Configuración de Base de Datos - RunRaids TCG

Esta guía te ayudará a configurar bases de datos separadas para desarrollo local y producción usando Supabase.

## 📋 Resumen de la Configuración

- **Desarrollo Local**: Base de datos Supabase separada para desarrollo
- **Producción**: Base de datos Supabase para producción en Vercel
- **Fallback**: SQLite local si no hay configuración de PostgreSQL

## 🏗️ Paso 1: Crear Proyecto en Supabase

### 1.1 Registro y Nuevo Proyecto
1. Ve a [supabase.com](https://supabase.com)
2. Crea una cuenta o inicia sesión
3. Haz clic en "New Project"
4. Configura:
   - **Name**: `runraids-tcg-dev` (para desarrollo)
   - **Database Password**: Genera una contraseña segura
   - **Region**: Selecciona la más cercana a ti
5. Espera a que se cree el proyecto (2-3 minutos)

### 1.2 Crear Segundo Proyecto para Producción
1. Repite el proceso anterior
2. Configura:
   - **Name**: `runraids-tcg-prod` (para producción)
   - **Database Password**: Genera otra contraseña segura
   - **Region**: La misma que el proyecto de desarrollo

## 🔧 Paso 2: Obtener URLs de Conexión

### 2.1 Para Desarrollo Local
1. En tu proyecto `runraids-tcg-dev`:
2. Ve a **Settings** > **Database**
3. Busca la sección **Connection pooling**
4. Copia la **Connection string** que se ve así:
   ```
   postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```

### 2.2 Para Producción
1. En tu proyecto `runraids-tcg-prod`:
2. Repite el mismo proceso
3. Copia la **Connection string** de producción

## ⚙️ Paso 3: Configuración Local

### 3.1 Crear archivo .env
Crea un archivo `.env` en la raíz del proyecto:

```env
# Django Configuration
SECRET_KEY=tu-clave-secreta-super-segura-aqui
DEBUG=True

# Database Configuration - DESARROLLO
DATABASE_URL=postgresql://postgres.xxxxx:[TU-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres

# Opcional: Configuración adicional
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3.2 Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3.3 Aplicar migraciones y cargar datos
```bash
# Aplicar migraciones
python manage.py migrate

# Cargar datos iniciales (incluye admin user: admin/admin)
python manage.py load_initial_data

# Verificar que todo funciona
python manage.py runserver
```

## 🚀 Paso 4: Configuración en Vercel (Producción)

### 4.1 Variables de Entorno en Vercel
1. Ve a tu proyecto en [vercel.com](https://vercel.com)
2. Ve a **Settings** > **Environment Variables**
3. Añade estas variables:

```
SECRET_KEY=tu-clave-secreta-super-segura-diferente
DEBUG=False
DATABASE_URL=postgresql://postgres.yyyyy:[TU-PASSWORD-PROD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

### 4.2 Re-deploy
1. Haz push de tus cambios:
   ```bash
   git add .
   git commit -m "Configure database setup"
   git push origin main
   ```
2. Vercel hará deploy automáticamente
3. Las migraciones y datos iniciales se aplicarán automáticamente

## 🔍 Paso 5: Verificación

### 5.1 Verificar Desarrollo Local
```bash
# Verificar conexión a la base de datos
python manage.py dbshell

# Verificar que los datos se cargaron
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.all()
>>> from core.models import Member
>>> Member.objects.all()
```

### 5.2 Verificar Producción
1. Ve a tu URL de Vercel
2. Accede a `/admin/` con `admin/admin`
3. Verifica que puedes ver los datos en el admin panel

## 🛠️ Comandos Útiles

### Gestión de Base de Datos
```bash
# Aplicar migraciones
python manage.py migrate

# Crear migraciones después de cambios en modelos
python manage.py makemigrations

# Cargar datos iniciales
python manage.py load_initial_data

# Acceder a la shell de Django
python manage.py shell

# Acceder directamente a la base de datos
python manage.py dbshell

# Crear superusuario manualmente
python manage.py createsuperuser
```

### Reset de Base de Datos (si es necesario)
```bash
# CUIDADO: Esto borra todos los datos
python manage.py flush

# Volver a aplicar migraciones
python manage.py migrate

# Cargar datos iniciales
python manage.py load_initial_data
```

## 🔐 Usuarios Creados Automáticamente

### Django Admin User
- **Usuario**: `admin`
- **Contraseña**: `admin`
- **Permisos**: Superusuario completo

### Usuarios del Juego
- **TestMember**: `555000001` / `test123`
- **TestPlayer1**: `123456789` / `testpass123`
- **TestPlayer2**: `987654321` / `testpass123`
- **AdminPlayer**: `111111111` / `adminpass123`

## 🚨 Troubleshooting

### Error: "relation does not exist"
```bash
python manage.py migrate
```

### Error: "no such table"
Estás usando SQLite en lugar de PostgreSQL. Verifica tu `DATABASE_URL`.

### Error de conexión a PostgreSQL
1. Verifica que la URL de Supabase sea correcta
2. Asegúrate de que la contraseña no tenga caracteres especiales sin escapar
3. Verifica que el proyecto de Supabase esté activo

### Los datos iniciales no se cargan
```bash
python manage.py load_initial_data --verbosity=2
```

## 📝 Notas Importantes

- **Separación de entornos**: Desarrollo y producción usan bases de datos completamente separadas
- **Datos de prueba**: Se cargan automáticamente en ambos entornos
- **Seguridad**: Usa contraseñas diferentes para desarrollo y producción
- **Backup**: Supabase hace backups automáticos, pero considera hacer backups manuales de datos importantes

---

¡Tu configuración de base de datos está lista! 🎮⚔️
