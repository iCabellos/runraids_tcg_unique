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
- Recursos: oro, comida, cristales... todos upgradables.
- Upgrades por tiempo con mejoras visuales y funcionales.

### ✅ Héroes y Clases
- Stats principales: HP, ATK físico/mágico, DEF, velocidad, stamina.
- Substats: daño elemental, robo de vida, reducción de daño, etc.
- Raza y clase: (ej. humano, deidad, bestia) x (soporte, daño, curandero).
- Habilidades pasivas automáticas y ataques definitivos.

### ✅ Sistema de Ítems
- Tipos: Armas, Anillos, Colgantes.
- Rareza ligada a la del héroe.
- Ítems únicos: otorgan efectos aleatorios o habilidades extra.
- Mejorables hasta nivel 10.

### ✅ Raids
- Duración: 10-30 min. por raid.
- Sistema por **oleadas**: 1-N enemigos por fase.
- Sistema de recompensa fija + aleatoria.
- Influencia del clima en batalla (RNG atmosférico).

---

## 🧠 Combate y Turnos Cooperativos

- El turno empieza con el héroe más rápido.
- Cada jugador actúa por orden de velocidad de sus héroes.
- Se aplican pasivas automáticas y luego se ejecutan habilidades.
- Turno finaliza al completar todas las acciones de los jugadores.
- Notificación al siguiente jugador → comienza nuevo turno.

---

## 📌 Estado del Desarrollo

### ✅ Completado
- 🔐 Sistema de Login
- 🛠️ Configuración de Backend Django
- 🗄️ Base de datos con modelos para Ciudad, Recursos, Héroes, Raids
- 👤 Administración vía Django Admin
- 📦 Configuración inicial para Vue frontend (SPA)

### 🔄 En Desarrollo
- ♻️ Sistema de turnos cooperativos
- ⚔️ Algoritmo de combate con habilidades pasivas
- 🌧️ Influencia del clima en batalla (RNG atmosférico)
- 🎲 Gacha de héroes
- 💬 Intercambio de ítems únicos entre jugadores
- 🛒 Tienda de ítems

---

## 🚀 Tecnologías Usadas

- 🐍 **Backend**: Django + Django REST Framework
- 🌐 **Frontend**: Vue 3 + Vite (desplegable en Vercel)
- 🗃️ **DB**: PostgreSQL
- 🔐 **Auth**: Login + sesiones (planeado: JWT)

---

## 🤝 Contribuir

¿Quieres unirte al equipo o ayudar en el desarrollo?

> Contáctanos por GitHub o redes sociales. Toda ayuda es bienvenida. 🙌

---

## 📅 Roadmap a Corto Plazo (v0.1 MVP)

- [X] Sistema básico de ciudad y recursos
- [ ] Vista de héroes y stats en el modal de la vista del campamento principal.
- [X] Primer raid funcional en frontend
- [X] Algoritmo de combate en backend
- [ ] Balance inicial de héroes e ítems
- [ ] Primera versión de arte estático para UI y héroes
- [ ] Sistema gacha desde el edificio del 'retrete'
- [ ] Fix de pequeños bugs y mejoras

---

_Disfruta de la estrategia, la cooperación y la progresión... ¡Bienvenido a **City Clash**!_

---

## 🧪 Cómo ejecutar y probar Raids asíncronas (Windows / PowerShell)

1) Clonar e instalar dependencias
- Requisitos: Python 3.11+, pip.
- Opcional: crear venv.
```
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2) Configurar entorno (.env) con SQLite local
Crea el archivo `.env` en la raíz del proyecto con:
```
DEBUG=True
SECRET_KEY=dev-secret
# SQLite local (para desarrollo rápido)
DATABASE_URL=sqlite:///db.sqlite3
```
Si prefieres PostgreSQL (p. ej. Supabase), define DATABASE_URL acorde.

3) Migrar base de datos y cargar datos iniciales
```
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata initial_data.json
# o usa el comando incluido para datos iniciales detallados
python manage.py load_initial_data
```

4) Arrancar el servidor
```
python manage.py runserver 127.0.0.1:8000
```

5) Iniciar sesión
- Abre http://127.0.0.1:8000/index/
- Usa uno de los usuarios de prueba definidos en datos iniciales (teléfono y contraseña).

6) Probar el sistema de Raids asíncronas
- Abre http://127.0.0.1:8000/raid/
- En dos pestañas (o dos navegadores) pulsa “Buscar raid”.
- La sala se llenará (max_players=2 por defecto), empezará la raid y verás:
  - Participantes y sus héroes con HP.
  - Enemigos y su HP.
  - Turno actual (actor héroe o enemigo).
  - Logs en tiempo casi real (polling cada 1s).
- Cuando sea tu turno, aparecerán botones “Atacar” junto a cada enemigo vivo. Pulsa para enviar la decisión a `/api/raid/decision/`.
- La IA enemiga actúa sola cuando le toca.
- Al terminar (todos héroes KO o todos enemigos KO) verás el log `finish` con `winner`.

7) Endpoints útiles (para debug)
- POST `/api/raid/matchmaking/join/` → une a matchmaking y devuelve `{room_id}`.
- GET `/api/raid/state/<room_id>/` → estado de la sala; además hace el “tick on read”.
- POST `/api/raid/decision/` con `room_id` y `target_enemy_id` → aplica tu ataque si es tu turno.

8) Solución de problemas
- No tengo DB: añade `DATABASE_URL=sqlite:///db.sqlite3` al `.env`.
- 401 unauthorized en API: asegúrate de iniciar sesión en `/index/` (sesión Django guarda `member_id`).
- No veo enemigos: necesitas tener al menos 1 `Enemy` en DB (cargado por initial_data). Revisa Django Admin `/admin/`.
- No aparecen botones de ataque: asegúrate de que sea tu turno (en el panel Turno verás actor_type=hero y tu member_id) y que tu héroe esté asignado (se autoasigna al llenar la sala).
- CSRF: los endpoints de raid ya están exentos (@csrf_exempt) para el MVP; si cambias eso, añade encabezados CSRF en fetch.

9) Ver decisiones en la DB
- En Django Admin, revisa `RaidDecisionLog` para ver todos los eventos: join, start, hero_attack, enemy_attack, finish.

10) Datos de apoyo
- La vista de prueba está en `core/templates/raid_room.html`.
- Lógica de raids en `core/services/raid_service.py`.
- Modelos en `core/models.py` (RaidRoom, RaidParticipant, RaidEnemyInstance, RaidTurn, RaidDecisionLog).
