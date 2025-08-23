# 🚀 Guía de Deployment en Vercel - RunRaids TCG

Esta guía te ayudará a deployar tu aplicación Django RunRaids en Vercel con PostgreSQL y CI/CD automático.

## 📋 Prerrequisitos

- Cuenta en [Vercel](https://vercel.com)
- Cuenta en [GitHub](https://github.com)
- Python 3.9+ instalado localmente
- Git instalado

## 🏗️ Estructura del Proyecto

El proyecto ha sido reestructurado para ser compatible con Vercel:

```
runraids_unique/
├── api/                    # Configuración Django para Vercel
│   ├── __init__.py
│   ├── settings.py        # Settings adaptado para producción
│   ├── urls.py           # URLs principales
│   └── wsgi.py           # WSGI app para Vercel
├── core/                  # Aplicación principal del juego
│   ├── management/       # Comandos personalizados
│   │   └── commands/
│   │       └── load_initial_data.py
│   ├── models.py
│   ├── views.py
│   └── ...
├── templates/            # Templates HTML
├── static/              # Archivos estáticos
├── initial_data.json    # Datos iniciales del juego
├── manage.py           # Django management
├── requirements.txt    # Dependencias Python
├── vercel.json        # Configuración de Vercel
├── build_files.sh     # Script de build
└── .env.example       # Variables de entorno ejemplo
```

## 🔧 Configuración Local

### 1. Clonar y configurar el proyecto

```bash
# Clonar el repositorio
git clone <tu-repositorio>
cd runraids_unique

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar variables de entorno locales

Crea un archivo `.env` basado en `.env.example`:

```bash
cp .env.example .env
```

Edita `.env` con tus valores:
```env
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
```

### 3. Configurar base de datos local

```bash
# Aplicar migraciones
python manage.py migrate

# Cargar datos iniciales
python manage.py load_initial_data

# Crear superusuario (opcional)
python manage.py createsuperuser
```

### 4. Probar localmente

```bash
python manage.py runserver
```

Visita `http://localhost:8000` para verificar que todo funciona.

## 🌐 Deployment en Vercel

### 1. Preparar el repositorio

```bash
# Asegúrate de que todos los cambios estén committeados
git add .
git commit -m "Preparar para deployment en Vercel"
git push origin main
```

### 2. Configurar Vercel

1. Ve a [vercel.com](https://vercel.com) e inicia sesión
2. Haz clic en "New Project"
3. Importa tu repositorio de GitHub
4. Vercel detectará automáticamente que es un proyecto Python
5. **IMPORTANTE**: En la configuración del proyecto, asegúrate de que:
   - Root Directory: `./` (raíz del proyecto)
   - Build Command: `bash build_files.sh`
   - Output Directory: `staticfiles_build`

### 3. Configurar variables de entorno en Vercel

En el dashboard de Vercel, ve a Settings > Environment Variables y añade:

```
SECRET_KEY=tu-clave-secreta-super-segura
DEBUG=False
POSTGRES_URL=postgresql://username:password@hostname:port/database
DJANGO_SETTINGS_MODULE=api.settings
```

### 4. Configurar base de datos PostgreSQL

#### Opción A: Vercel Postgres (Recomendado)

1. En tu proyecto de Vercel, ve a la pestaña "Storage"
2. Haz clic en "Create Database" > "Postgres"
3. Sigue las instrucciones para crear la base de datos
4. Vercel añadirá automáticamente la variable `POSTGRES_URL`

#### Opción B: Proveedor externo

Puedes usar servicios como:
- [Neon](https://neon.tech) (Gratis)
- [Supabase](https://supabase.com) (Gratis)
- [Railway](https://railway.app) (Gratis)
- [ElephantSQL](https://www.elephantsql.com) (Gratis)

### 5. Deploy automático

Una vez configurado:

1. Vercel ejecutará automáticamente el build
2. Se aplicarán las migraciones
3. Se cargarán los datos iniciales
4. La aplicación estará disponible en tu URL de Vercel

## 🔄 CI/CD Automático

El proyecto está configurado para CI/CD automático:

- **Push a main**: Deploy automático a producción
- **Pull Requests**: Preview deployments automáticos
- **Build automático**: Migraciones y carga de datos inicial

## 🎮 Datos de Prueba

La aplicación incluye datos de prueba que se cargan automáticamente:

### Usuarios de prueba:
- **Teléfono**: `123456789` | **Contraseña**: `testpass123`
- **Teléfono**: `987654321` | **Contraseña**: `testpass123`
- **Teléfono**: `111111111` | **Contraseña**: `adminpass123` (Admin)

### Contenido incluido:
- 5 tipos de recursos (Oro, Madera, Piedra, Hierro, Comida)
- 6 tipos de edificios
- 5 raridades de héroes
- 5 habilidades básicas
- 5 héroes con diferentes raridades
- 3 enemigos
- Costos de mejora de edificios

## 🛠️ Comandos Útiles

```bash
# Cargar datos iniciales manualmente
python manage.py load_initial_data

# Aplicar migraciones
python manage.py migrate

# Recopilar archivos estáticos
python manage.py collectstatic

# Crear superusuario
python manage.py createsuperuser

# Ejecutar tests
python manage.py test
```

## 🔍 Troubleshooting

### Error de migraciones
```bash
# Resetear migraciones si es necesario
python manage.py migrate --fake-initial
```

### Error de archivos estáticos
```bash
# Recopilar archivos estáticos
python manage.py collectstatic --clear --noinput
```

### Error de base de datos
- Verifica que `POSTGRES_URL` esté correctamente configurada
- Asegúrate de que la base de datos esté accesible

### Error de build en Vercel
- Revisa los logs en el dashboard de Vercel
- Verifica que todas las variables de entorno estén configuradas
- Asegúrate de que `requirements.txt` esté actualizado

## 🚀 Próximos Pasos

Una vez deployado, puedes:

1. **Configurar dominio personalizado** en Vercel
2. **Añadir más datos** usando el admin de Django
3. **Configurar monitoreo** con herramientas como Sentry
4. **Optimizar rendimiento** con caching
5. **Añadir tests automatizados** con GitHub Actions

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs en Vercel Dashboard
2. Verifica la configuración de variables de entorno
3. Asegúrate de que la base de datos esté funcionando
4. Consulta la documentación de [Vercel](https://vercel.com/docs)

---

¡Tu aplicación RunRaids TCG está lista para conquistar el mundo! 🎮⚔️
