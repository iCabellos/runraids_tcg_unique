# 🌆 City Clash - Juego de Gestión con Héroes y Raids Cooperativos PvE

## 🏆 Idea Principal

City Clash es un **juego RPG de gestión de ciudad y raids cooperativos** por turnos, con héroes legendarios y míticos, y un sistema de ítems únicos. El jugador mejora su ciudad, colecciona héroes, equipa ítems y se une a otros jugadores para enfrentarse en raids épicas por oleadas.

### 🔹 Características Generales
- 🎮 Juego cooperativo hasta **6 jugadores** por raid.
- 🦸‍♂️ **Héroes autocasteados** con habilidades pasivas y definitivas.
- 🕹️ **Combates por turnos** con sistema de velocidad y stamina.
- 🏗️ Construye tu ciudad y produce recursos como oro o comida.
- 🎲 Sistema **gacha** para conseguir héroes con rarezas únicas.
- 🎁 Ítems equipables que potencian características y pasivas.

---

## 🎯 Características Detalladas

### ✅ Ciudad y Recursos
- Sistema de edificios: minas, cuarteles, torres de magia...
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
