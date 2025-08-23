# 🎮 RunRaids TCG - Juego de Cartas Coleccionables

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/tu-usuario/runraids-tcg)

Un juego de cartas coleccionables (TCG) desarrollado con Django, diseñado para ser deployado en Vercel con PostgreSQL y preparado para futuras integraciones con Unity, UE5 y otras plataformas.

## 🌟 Características

- 🏰 **Sistema de Edificios**: Construye y mejora edificios en tu campamento
- ⚔️ **Combate por Turnos**: Sistema de combate estratégico con habilidades
- 🦸 **Héroes Coleccionables**: Diferentes raridades y habilidades únicas
- 🏛️ **Sistema de Alianzas**: Únete a otros jugadores y construye juntos
- 💰 **Economía de Recursos**: Gestiona oro, madera, piedra, hierro y comida
- 🎲 **Sistema de Raridades**: Desde común hasta legendario
- 📱 **API-First**: Lógica de negocio separada para futuras integraciones

## 🚀 Demo en Vivo

🔗 **[Ver Demo](https://tu-app.vercel.app)**

### Usuarios de Prueba:
- **Teléfono**: `123456789` | **Contraseña**: `testpass123`
- **Teléfono**: `987654321` | **Contraseña**: `testpass123`
- **Teléfono**: `111111111` | **Contraseña**: `adminpass123` (Admin)

## 🛠️ Tecnologías

- **Backend**: Django 5.1.6 + Django REST Framework
- **Base de Datos**: PostgreSQL (Vercel Postgres)
- **Frontend**: HTML5 + Bootstrap + JavaScript
- **Deployment**: Vercel con CI/CD automático
- **Autenticación**: Sistema de sesiones Django

## 📦 Instalación Rápida

### Opción 1: Deploy Directo en Vercel (Recomendado)

1. Haz clic en el botón "Deploy with Vercel" arriba
2. Conecta tu cuenta de GitHub
3. Configura las variables de entorno
4. ¡Listo! Tu aplicación estará funcionando en minutos

### Opción 2: Desarrollo Local

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/runraids-tcg.git
cd runraids-tcg

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
python manage.py migrate
python manage.py load_initial_data

# Ejecutar servidor
python manage.py runserver
```

## 🎯 Arquitectura API-First

El proyecto está diseñado con una arquitectura API-First que permite:

- **Separación clara** entre lógica de negocio y presentación
- **Fácil integración** con Unity, UE5, o cualquier cliente
- **Escalabilidad** para múltiples plataformas
- **Mantenimiento** simplificado del código

### Estructura del Proyecto

```
runraids_unique/
├── api/                    # Configuración Django para Vercel
├── core/                   # Lógica de negocio principal
│   ├── models.py          # Modelos de datos
│   ├── views.py           # Lógica de vistas
│   ├── services/          # Servicios de negocio
│   └── management/        # Comandos personalizados
├── templates/             # Templates HTML (solo presentación)
├── static/               # Archivos estáticos
└── initial_data.json     # Datos iniciales del juego
```

## 🎮 Funcionalidades del Juego

### Sistema de Recursos
- **Oro**: Moneda principal
- **Madera**: Construcción básica
- **Piedra**: Construcción avanzada
- **Hierro**: Armas y herramientas
- **Comida**: Mantenimiento de héroes

### Tipos de Edificios
- **Campamento**: Base principal
- **Cuarteles**: Entrenamiento de héroes
- **Granja**: Producción de comida
- **Mina**: Extracción de hierro
- **Aserradero**: Producción de madera
- **Cantera**: Extracción de piedra

### Sistema de Héroes
- **5 Raridades**: Común, Poco común, Raro, Épico, Legendario
- **Habilidades Únicas**: Ataque, Curación, Defensa
- **Sistema de Experiencia**: Mejora tus héroes
- **Combate Estratégico**: Usa habilidades sabiamente

## 🚀 Deployment

Para instrucciones detalladas de deployment, consulta [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md).

### Deploy Rápido en Vercel

1. Fork este repositorio
2. Conecta con Vercel
3. Configura PostgreSQL
4. Añade variables de entorno
5. ¡Deploy automático!

## 🔮 Roadmap

### v1.0 - MVP Actual ✅
- [x] Sistema básico de recursos
- [x] Edificios y mejoras
- [x] Héroes y combate
- [x] Sistema de alianzas
- [x] Deployment en Vercel

### v1.1 - Próximas Funcionalidades
- [ ] API REST completa
- [ ] Sistema de intercambio
- [ ] Eventos temporales
- [ ] Notificaciones push
- [ ] Modo multijugador en tiempo real

### v2.0 - Integración Multiplataforma
- [ ] SDK para Unity
- [ ] SDK para Unreal Engine
- [ ] API GraphQL
- [ ] Sistema de matchmaking
- [ ] Torneos automatizados

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🙏 Agradecimientos

- [Django](https://djangoproject.com/) - Framework web
- [Vercel](https://vercel.com/) - Platform de deployment
- [Bootstrap](https://getbootstrap.com/) - Framework CSS
- [PostgreSQL](https://postgresql.org/) - Base de datos

---

**¿Te gusta el proyecto?** ⭐ ¡Dale una estrella en GitHub!

**¿Tienes preguntas?** 💬 Abre un issue o contacta al equipo.

**¿Quieres contribuir?** 🚀 ¡Revisa nuestro roadmap y únete al desarrollo!
