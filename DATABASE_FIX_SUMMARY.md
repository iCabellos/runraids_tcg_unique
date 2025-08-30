# 🔧 Corrección de Problemas de Base de Datos

## ✅ Problemas Solucionados

### 1. **Configuración de Base de Datos**
- ✅ Soporte para `DATABASE_URL` (Supabase) y `POSTGRES_URL` (Vercel)
- ✅ Fallback automático a SQLite si no hay PostgreSQL configurado
- ✅ Mensajes informativos sobre qué base de datos se está usando

### 2. **Datos Iniciales Mejorados**
- ✅ Usuario admin de Django: `admin/admin`
- ✅ Usuario member de prueba: `555000001/test123`
- ✅ Usuarios existentes mantenidos
- ✅ Creación automática de usuarios Django admin

### 3. **Comandos de Gestión Mejorados**
- ✅ `load_initial_data`: Manejo robusto de errores
- ✅ `check_database`: Nuevo comando para verificar configuración
- ✅ Scripts de setup automático

### 4. **Scripts de Automatización**
- ✅ `setup_database.py`: Setup completo local
- ✅ `vercel_build.py`: Build automático para Vercel

## 🚀 Cómo Usar la Nueva Configuración

### Para Desarrollo Local

#### 1. Configurar Supabase
```bash
# Sigue la guía completa
cat DATABASE_SETUP_GUIDE.md
```

#### 2. Crear archivo .env
```env
SECRET_KEY=tu-clave-secreta
DEBUG=True
DATABASE_URL=postgresql://postgres.xxxxx:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

#### 3. Setup automático
```bash
# Opción A: Script automático (recomendado)
python setup_database.py

# Opción B: Manual
python manage.py migrate
python manage.py load_initial_data
python manage.py check_database
```

#### 4. Verificar funcionamiento
```bash
python manage.py runserver
# Ve a http://localhost:8000/admin/ (admin/admin)
```

### Para Producción en Vercel

#### 1. Variables de Entorno
En Vercel Dashboard > Settings > Environment Variables:
```
SECRET_KEY=clave-secreta-diferente-para-prod
DEBUG=False
DATABASE_URL=postgresql://postgres.yyyyy:[PASSWORD-PROD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

#### 2. Deploy
```bash
git add .
git commit -m "Database configuration fixed"
git push origin main
```

#### 3. Verificar
- Ve a tu URL de Vercel
- Accede a `/admin/` con `admin/admin`
- Verifica que el juego funciona

## 🔍 Comandos de Verificación

### Verificar Conexión de Base de Datos
```bash
python manage.py check_database
```

### Verificar Datos Cargados
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.filter(is_superuser=True)
>>> from core.models import Member
>>> Member.objects.all()
```

### Re-cargar Datos (si es necesario)
```bash
python manage.py load_initial_data
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

## 🛠️ Troubleshooting

### "No module named 'core'"
```bash
# Verifica que estás en el directorio correcto
ls -la  # Deberías ver manage.py y core/
```

### "relation does not exist"
```bash
python manage.py migrate
```

### "Database connection failed"
1. Verifica tu `DATABASE_URL` en `.env`
2. Asegúrate de que Supabase esté activo
3. Verifica la contraseña

### Los datos no se cargan
```bash
python manage.py load_initial_data --verbosity=2
```

### Error en Vercel
1. Revisa los logs en Vercel Dashboard
2. Verifica las variables de entorno
3. Asegúrate de que la base de datos de producción esté configurada

## 📝 Archivos Importantes

- `DATABASE_SETUP_GUIDE.md`: Guía completa de configuración
- `setup_database.py`: Script de setup automático
- `api/settings.py`: Configuración de base de datos
- `core/management/commands/load_initial_data.py`: Carga de datos
- `core/management/commands/check_database.py`: Verificación
- `.env.example`: Ejemplo de configuración

## 🎯 Próximos Pasos

1. **Configura Supabase** siguiendo `DATABASE_SETUP_GUIDE.md`
2. **Ejecuta setup local** con `python setup_database.py`
3. **Configura producción** en Vercel
4. **Verifica que todo funciona** en ambos entornos

---

¡Tu configuración de base de datos está completamente arreglada! 🎮⚔️
