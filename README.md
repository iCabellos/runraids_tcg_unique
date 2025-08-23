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

- [ ] Sistema básico de ciudad y recursos
- [ ] Vista de héroes y stats
- [ ] Primer raid funcional en frontend
- [ ] Algoritmo de combate en backend
- [ ] Balance inicial de héroes e ítems
- [ ] Primera versión de arte estático para UI y héroes

---

_Disfruta de la estrategia, la cooperación y la progresión... ¡Bienvenido a **City Clash**!_
