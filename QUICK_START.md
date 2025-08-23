# 🚀 Quick Start - RunRaids TCG en Vercel

## ⚡ Deploy en 5 minutos

### 1. Preparar el repositorio
```bash
git add .
git commit -m "Ready for Vercel deployment"
git push origin main
```

### 2. Deploy en Vercel
1. Ve a [vercel.com](https://vercel.com)
2. Haz clic en "New Project"
3. Importa tu repositorio
4. Configura:
   - **Root Directory**: `./`
   - **Build Command**: `bash build_files.sh`
   - **Output Directory**: `staticfiles_build`

### 3. Variables de entorno requeridas
```env
SECRET_KEY=tu-clave-secreta-super-segura
DEBUG=False
POSTGRES_URL=postgresql://user:pass@host:port/db
DJANGO_SETTINGS_MODULE=api.settings
```

### 4. Configurar PostgreSQL
- **Opción A**: Vercel Postgres (Storage > Create Database)
- **Opción B**: [Neon.tech](https://neon.tech) (Gratis)
- **Opción C**: [Supabase](https://supabase.com) (Gratis)

### 5. ¡Listo!
Tu aplicación estará disponible en: `https://tu-proyecto.vercel.app`

## 🎮 Usuarios de prueba
- **Teléfono**: `123456789` | **Contraseña**: `testpass123`
- **Teléfono**: `987654321` | **Contraseña**: `testpass123`
- **Teléfono**: `111111111` | **Contraseña**: `adminpass123`

## 🛠️ Comandos útiles

### Desarrollo local
```bash
python manage.py runserver
python manage.py migrate
python manage.py load_initial_data
python manage.py createsuperuser
```

### Troubleshooting
```bash
# Si hay problemas con migraciones
python manage.py migrate --fake-initial

# Si hay problemas con archivos estáticos
python manage.py collectstatic --clear --noinput

# Ver logs en Vercel
vercel logs
```

## 📚 Documentación completa
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Guía completa
- [README_NEW.md](./README_NEW.md) - Documentación del proyecto

---

¡Tu juego RunRaids TCG estará funcionando en minutos! 🎮⚔️
