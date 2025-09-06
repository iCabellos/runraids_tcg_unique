from django.db import transaction
from django.utils.timezone import now
from django.http import JsonResponse
from core.models import (
    RaidRoom, RaidParticipant, RaidEnemyInstance, RaidTurn, RaidDecisionLog,
    Member, PlayerHero, Enemy, Raid, RaidWave, RaidEnemy, Team
)
import random

class RaidError(Exception):
    pass


def matchmaking_join(member: Member, raid: Raid = None, team: Team = None) -> RaidRoom:
    """
    Unirse al matchmaking para una raid específica.
    Busca una sala existente o crea una nueva.
    """
    if not raid:
        raise RaidError("Se requiere especificar una raid")

    if not team:
        team = Team.objects.filter(owner=member, is_active=True).first()
        if not team:
            raise RaidError("Necesitas un equipo para participar en raids")

    # Verificar que el equipo tenga al menos un héroe vivo
    alive_heroes = team.slots.filter(player_hero__current_hp__gt=0).count()
    if alive_heroes == 0:
        raise RaidError("Todos tus héroes están muertos. Cúralos antes de participar en raids.")

    # Buscar sala existente para esta raid específica
    from django.db.models import Count
    room = (RaidRoom.objects
            .filter(state="waiting", raid=raid)
            .annotate(participant_count=Count('participants'))
            .filter(participant_count__lt=raid.max_players)
            .order_by("created_at")
            .first())

    if not room:
        # Crear nueva sala
        room = RaidRoom.objects.create(
            owner=member,
            raid=raid,
            max_players=raid.max_players,
            random_seed=random.randint(1, 10_000),
            name=f"Sala de {raid.name}"
        )

    # Verificar que el miembro no esté ya en la sala
    if room.participants.filter(member=member).exists():
        return room

    # Añadir participante con su equipo (por ahora solo el primer héroe del equipo)
    team_hero = team.slots.first()
    if not team_hero:
        raise RaidError("Tu equipo no tiene héroes asignados")

    # Asignar color basado en el orden de llegada
    participant_count = room.participants.count()
    player_color = (participant_count % 4) + 1  # Colores 1-4

    p = RaidParticipant.objects.create(
        room=room,
        member=member,
        hero=team_hero.player_hero,
        is_ready=True,
        player_color=player_color
    )

    RaidDecisionLog.objects.create(
        room=room,
        participant=None,
        action_type="join",
        payload={"member_id": member.id, "hero_id": team_hero.player_hero.id, "team_id": team.id}
    )

    # Si la sala está llena, iniciar automáticamente
    if room.participants.count() >= room.max_players:
        start_structured_raid(room)

    return room


def start_structured_raid(room: RaidRoom):
    """Iniciar una raid estructurada con oleadas definidas"""
    if room.state not in ["waiting", "ready"]:
        return

    if not room.raid:
        raise RaidError("La sala no tiene una raid asignada")

    # Inicializar la primera oleada
    room.wave_index = 0
    spawn_wave_enemies(room)

    # Build first turn order
    build_turn_order(room)
    room.state = "in_progress"
    room.last_tick_at = now()

    # Set expiration in 30 minutes for structured raids
    from datetime import timedelta
    room.expires_at = (room.created_at or now()) + timedelta(minutes=30)
    room.closed = False
    room.save(update_fields=["state", "last_tick_at", "expires_at", "closed", "wave_index"])

    RaidDecisionLog.objects.create(
        room=room,
        action_type="start",
        payload={"raid_id": room.raid.id, "wave_index": room.wave_index}
    )


def spawn_wave_enemies(room: RaidRoom):
    """Generar enemigos para la oleada actual"""
    if not room.raid:
        return

    try:
        wave = room.raid.waves.get(wave_number=room.wave_index + 1)  # waves are 1-indexed
    except RaidWave.DoesNotExist:
        # No more waves, raid completed
        finish_room(room, winner="heroes")
        return

    # Clear existing enemies
    room.enemies.all().delete()

    # Spawn enemies for this wave
    for raid_enemy in wave.enemies.all():
        for _ in range(raid_enemy.quantity):
            enemy = raid_enemy.enemy
            level_mod = raid_enemy.level_modifier

            RaidEnemyInstance.objects.create(
                room=room,
                enemy=enemy,
                max_hp=int(enemy.base_hp * level_mod),
                current_hp=int(enemy.base_hp * level_mod),
                speed=int(enemy.speed * level_mod),
            )

    RaidDecisionLog.objects.create(
        room=room,
        action_type="wave_start",
        payload={"wave_number": wave.wave_number, "wave_name": wave.name}
    )


def start_raid(room: RaidRoom, enemy: Enemy | None = None):
    """Función legacy para raids simples (compatibilidad)"""
    if room.state not in ["waiting", "ready"]:
        return
    rng = random.Random(room.random_seed or int(now().timestamp()))
    # Create a simple single-enemy wave for test
    enemy = enemy or Enemy.objects.order_by("?").first()
    if not enemy:
        raise RaidError("No enemies defined")
    RaidEnemyInstance.objects.create(
        room=room,
        enemy=enemy,
        max_hp=enemy.base_hp,
        current_hp=enemy.base_hp,
        speed=enemy.speed,
    )
    # Build first turn order
    build_turn_order(room)
    room.state = "in_progress"
    room.last_tick_at = now()
    # Set expiration in 20 minutes
    from datetime import timedelta
    room.expires_at = (room.created_at or now()) + timedelta(minutes=20)
    room.closed = False
    room.save(update_fields=["state", "last_tick_at", "expires_at", "closed"])
    RaidDecisionLog.objects.create(room=room, action_type="start", payload={"enemy_id": enemy.id})


def build_turn_order(room: RaidRoom):
    """
    Construir orden de turnos basado en velocidad de TODOS los héroes y enemigos.
    Cada héroe individual tiene su propio turno, no por jugador.
    """
    from core.models import Team, RaidTurn

    # Clear existing unresolved future turns
    room.turns.all().delete()
    order = []

    # Añadir TODOS los héroes vivos de TODOS los jugadores
    for participant in room.participants.select_related("member").all():
        team = Team.objects.filter(owner=participant.member, is_active=True).first()
        if team:
            # Obtener todos los héroes vivos del equipo
            team_slots = team.slots.select_related('player_hero__hero').filter(
                player_hero__current_hp__gt=0
            )
            for slot in team_slots:
                hero = slot.player_hero
                speed = hero.s_speed()
                order.append(("hero", speed, participant, hero))

    # Añadir todos los enemigos vivos
    for enemy in room.enemies.all():
        if enemy.is_alive:
            order.append(("enemy", enemy.speed, enemy, None))

    # Ordenar por velocidad (mayor velocidad = primero)
    order.sort(key=lambda x: x[1], reverse=True)

    # Crear turnos en orden de velocidad
    for idx, (actor_type, speed, obj, hero) in enumerate(order):
        if actor_type == "hero":
            # obj es el participant, hero es el PlayerHero específico
            RaidTurn.objects.create(
                room=room,
                index=idx,
                actor_type="hero",
                participant=obj,
                hero_instance=hero  # Necesitaremos añadir este campo al modelo
            )
        else:
            # obj es el enemy instance
            RaidTurn.objects.create(
                room=room,
                index=idx,
                actor_type="enemy",
                enemy_instance=obj
            )


def get_current_turn(room: RaidRoom):
    return room.turns.filter(resolved=False).order_by("index").first()


def process_tick(room: RaidRoom):
    """Procesar tick de la raid - se ejecuta cada segundo"""
    from django.utils.timezone import now as tz_now

    # Auto-ready después de 5 segundos en waiting
    if room.state == "waiting":
        time_waiting = (tz_now() - room.created_at).total_seconds()
        if time_waiting >= 5:
            room.state = "ready"
            room.save(update_fields=["state"])
            RaidDecisionLog.objects.create(
                room=room,
                action_type="auto_ready",
                payload={"seconds_waited": time_waiting}
            )
        return

    # Auto-start después de 4 minutos en ready
    if room.state == "ready":
        time_waiting = (tz_now() - room.created_at).total_seconds()
        if time_waiting >= 240:  # 4 minutos = 240 segundos
            # Auto-iniciar la raid
            if room.raid:
                start_structured_raid(room)
            else:
                from core.models import Enemy
                enemy = Enemy.objects.order_by("?").first()
                if enemy:
                    start_raid(room, enemy=enemy)

            RaidDecisionLog.objects.create(
                room=room,
                action_type="auto_start",
                payload={"seconds_waited": time_waiting, "reason": "timeout_4min"}
            )
        return

    if room.state != "in_progress":
        return

    # Check timeout
    if room.expires_at and not room.closed and tz_now() >= room.expires_at:
        force_close_room(room)
        return

    # Verificar si todos los héroes están muertos
    if not room.participants.filter(is_alive=True).exists():
        finish_room(room, winner="enemies")
        return

    # Verificar si todos los enemigos están muertos (para raids estructuradas)
    if room.raid and not room.enemies.filter(is_alive=True).exists():
        check_wave_completion(room)
        return

    # Procesar turno actual
    turn = get_current_turn(room)
    if not turn:
        # rebuild cycle
        build_turn_order(room)
        turn = get_current_turn(room)
        if not turn:
            return

    # Enemy AI acts automatically
    if turn.actor_type == "enemy":
        if turn.enemy_instance and turn.enemy_instance.is_alive:
            enemy_attack(room, turn)
        else:
            # Enemy is dead, skip turn
            turn.resolved = True
            turn.save()
            RaidDecisionLog.objects.create(
                room=room,
                turn=turn,
                participant=None,
                actor="Sistema",
                action_type="skip_dead_enemy",
                payload={"reason": "enemy_dead", "enemy_id": turn.enemy_instance_id}
            )

    # Auto-skip turns for dead heroes or participants
    elif turn.actor_type == "hero":
        # Verificar si el héroe específico está muerto
        hero_alive = True
        if turn.hero_instance:
            hero_alive = turn.hero_instance.current_hp > 0
        elif turn.participant:
            # Fallback para compatibilidad con turnos antiguos
            hero_alive = turn.participant.is_alive and turn.participant.hero and turn.participant.hero.current_hp > 0

        if not hero_alive:
            turn.resolved = True
            turn.save()
            RaidDecisionLog.objects.create(
                room=room,
                turn=turn,
                participant=turn.participant,
                action_type="skip_dead",
                payload={
                    "reason": "hero_dead",
                    "hero_id": turn.hero_instance.id if turn.hero_instance else None
                }
            )


def enemy_attack(room: RaidRoom, turn: RaidTurn):
    import random

    # Verificar que el enemigo esté vivo
    enemy = turn.enemy_instance
    if not enemy or not enemy.is_alive:
        turn.resolved = True
        turn.save()
        return

    # Buscar TODOS los héroes vivos de TODOS los jugadores
    from core.models import Team, TeamSlot

    alive_heroes = []
    participants = room.participants.select_related("member").all()

    for participant in participants:
        # Obtener equipo del jugador
        team = Team.objects.filter(owner=participant.member, is_active=True).first()
        if team:
            # Obtener todos los héroes vivos del equipo
            team_slots = team.slots.select_related('player_hero__hero').filter(
                player_hero__current_hp__gt=0
            )
            for slot in team_slots:
                alive_heroes.append({
                    'participant': participant,
                    'hero': slot.player_hero,
                    'slot': slot
                })

    if not alive_heroes:
        finish_room(room, winner="enemies")
        return

    # Seleccionar héroe aleatorio de todos los disponibles
    target_data = random.choice(alive_heroes)
    target_participant = target_data['participant']
    target_hero = target_data['hero']

    # Calcular daño
    base_damage = enemy.enemy.attack if hasattr(enemy.enemy, 'attack') else 10
    dmg = max(1, int(base_damage * random.uniform(0.8, 1.2)))  # Variación de daño

    # Aplicar daño al héroe
    old_hp = target_hero.current_hp
    target_hero.current_hp = max(0, target_hero.current_hp - dmg)
    target_hero.save()

    # Verificar si el héroe murió
    hero_died = target_hero.current_hp <= 0
    if hero_died:
        # Log de muerte del héroe
        RaidDecisionLog.objects.create(
            room=room,
            turn=turn,
            participant=None,
            actor=enemy.enemy.name,
            action_type="hero_killed",
            payload={
                "target_member_id": target_participant.member_id,
                "target_hero": target_hero.hero.name,
                "dmg": dmg,
                "old_hp": old_hp
            }
        )

        # Verificar si el participante se queda sin héroes vivos
        team = Team.objects.filter(owner=target_participant.member, is_active=True).first()
        if team:
            alive_heroes_count = team.slots.filter(player_hero__current_hp__gt=0).count()
            if alive_heroes_count == 0 and target_participant.is_alive:
                target_participant.is_alive = False
                target_participant.save()

                RaidDecisionLog.objects.create(
                    room=room,
                    turn=turn,
                    participant=None,
                    actor=enemy.enemy.name,
                    action_type="participant_eliminated",
                    payload={
                        "member_id": target_participant.member_id,
                        "reason": "all_heroes_dead"
                    }
                )

    # Log del ataque (solo si el héroe no murió, para evitar duplicados)
    if not hero_died:
        RaidDecisionLog.objects.create(
            room=room,
            turn=turn,
            participant=None,
            actor=enemy.enemy.name,
            action_type="enemy_attack",
            payload={
                "target_member_id": target_participant.member_id,
                "target_hero": target_hero.hero.name,
                "dmg": dmg,
                "remaining_hp": target_hero.current_hp
            }
        )

    # Resolver turno
    turn.resolved = True
    turn.save()

    # Verificar condiciones de victoria/derrota
    if not room.participants.filter(is_alive=True).exists():
        finish_room(room, winner="enemies")
        return

    # Para raids estructuradas, verificar si se completó la oleada
    if room.raid and not room.enemies.filter(is_alive=True).exists():
        check_wave_completion(room)


def submit_player_decision(member: Member, room: RaidRoom, ability_id: int | None = None, target_enemy_id: int | None = None):
    if room.state != "in_progress":
        raise RaidError("Raid no iniciada")

    # Verificar que el miembro esté en la raid
    part = RaidParticipant.objects.filter(room=room, member=member).first()
    if not part:
        raise RaidError("No estás en esta raid")

    turn = get_current_turn(room)
    if not turn or turn.actor_type != "hero":
        raise RaidError("No es turno de un héroe")

    # Verificar que sea el turno del jugador correcto
    if turn.participant_id != part.id:
        raise RaidError("No es tu turno")

    # Obtener el héroe específico que tiene el turno
    attacking_hero = None
    if turn.hero_instance:
        # Nuevo sistema: héroe específico
        attacking_hero = turn.hero_instance
        if attacking_hero.current_hp <= 0:
            raise RaidError("El héroe está muerto")
    else:
        # Fallback para compatibilidad
        if not part.hero or part.hero.current_hp <= 0:
            raise RaidError("Tu héroe está muerto")
        attacking_hero = part.hero

    # Seleccionar enemigo objetivo
    enemy_inst = room.enemies.filter(id=target_enemy_id, is_alive=True).first() if target_enemy_id else room.enemies.filter(is_alive=True).first()
    if not enemy_inst:
        raise RaidError("No hay enemigo vivo")

    # Calcular daño
    hero_atk = attacking_hero.s_atk_phy() + attacking_hero.s_atk_mag()
    dmg = max(1, int(hero_atk * 0.4))

    # Aplicar daño al enemigo
    enemy_inst.current_hp = max(0, enemy_inst.current_hp - dmg)
    if enemy_inst.current_hp == 0:
        enemy_inst.is_alive = False
    enemy_inst.save()

    # Log del ataque
    RaidDecisionLog.objects.create(
        room=room,
        turn=turn,
        participant=part,
        actor=attacking_hero.hero.name,
        action_type="hero_attack",
        payload={
            "enemy_id": enemy_inst.id,
            "dmg": dmg,
            "hero_id": attacking_hero.id,
            "enemy_remaining_hp": enemy_inst.current_hp
        }
    )

    # Resolver turno
    turn.resolved = True
    turn.save()

    # Verificar si la oleada está completada (para raids estructuradas)
    if room.raid:
        check_wave_completion(room)
    else:
        # Raid legacy: verificar si todos los enemigos están muertos
        if not room.enemies.filter(is_alive=True).exists():
            finish_room(room, winner="heroes")


def start_solo_raid(member: Member, raid: Raid = None, team: Team = None, enemy: Enemy = None) -> RaidRoom:
    """Iniciar una raid en solitario"""
    if raid:
        # Raid estructurada
        if not team:
            team = Team.objects.filter(owner=member, is_active=True).first()
            if not team:
                raise RaidError("Necesitas un equipo para participar en raids")

        team_hero = team.slots.first()
        if not team_hero:
            raise RaidError("Tu equipo no tiene héroes asignados")

        room = RaidRoom.objects.create(
            owner=member,
            raid=raid,
            max_players=1,
            random_seed=random.randint(1, 10_000),
            name=f"Solo: {raid.name}"
        )
        RaidParticipant.objects.create(
            room=room,
            member=member,
            hero=team_hero.player_hero,
            is_ready=True,
            is_alive=True
        )
        start_structured_raid(room)
    else:
        # Raid legacy con enemigo simple
        if not enemy:
            raise RaidError("Se requiere especificar un enemigo para raids simples")
        if not team:
            team = Team.objects.filter(owner=member, is_active=True).first()

        hero = team.slots.first().player_hero if team and team.slots.exists() else None
        if not hero:
            raise RaidError("Necesitas un héroe para participar")

        room = RaidRoom.objects.create(owner=member, max_players=1, random_seed=random.randint(1, 10_000))
        RaidParticipant.objects.create(room=room, member=member, hero=hero, is_ready=True, is_alive=True)
        start_raid(room, enemy=enemy)

    return room


def check_wave_completion(room: RaidRoom):
    """Verificar si la oleada actual está completada y avanzar si es necesario"""
    if not room.raid:
        return  # Raid legacy, no hay oleadas

    # Verificar si todos los enemigos están muertos
    if room.enemies.filter(is_alive=True).exists():
        return  # Aún hay enemigos vivos

    # Oleada completada, avanzar a la siguiente
    room.wave_index += 1
    room.save(update_fields=["wave_index"])

    # Intentar generar la siguiente oleada
    spawn_wave_enemies(room)

    # Si no hay más oleadas, la raid está completada
    if not room.enemies.exists():
        finish_room(room, winner="heroes")
    else:
        # Reconstruir orden de turnos para la nueva oleada
        build_turn_order(room)


def finish_room(room: RaidRoom, winner: str):
    room.state = "finished"
    room.save(update_fields=["state"])
    RaidDecisionLog.objects.create(room=room, action_type="finish", payload={"winner": winner})


def process_all_active_raids():
    """Procesar todas las raids activas - para llamar desde un cron job o similar"""
    active_rooms = RaidRoom.objects.filter(state="in_progress", closed=False)
    for room in active_rooms:
        try:
            process_tick(room)
        except Exception as e:
            # Log error but continue processing other rooms
            import logging
            logging.error(f"Error processing raid room {room.id}: {e}")


def auto_start_full_rooms():
    """Auto-iniciar salas que estén llenas y listas"""
    from core.models import Team

    # Buscar salas ready o waiting con suficientes jugadores
    ready_rooms = RaidRoom.objects.filter(
        state__in=["ready", "waiting"]
    ).prefetch_related('participants')

    for room in ready_rooms:
        # Para salas ready, pueden iniciarse con cualquier número de jugadores (1-4)
        # Para salas waiting, solo si están llenas
        can_start = (
            room.state == "ready" and room.participants.count() >= 1
        ) or (
            room.state == "waiting" and room.participants.count() >= room.max_players
        )

        if can_start:
            # Verificar que todos tengan héroes asignados
            all_ready = True
            for p in room.participants.all():
                if not p.hero:
                    # Asignar primer héroe disponible del equipo
                    team = Team.objects.filter(owner=p.member, is_active=True).first()
                    if team and team.slots.exists():
                        p.hero = team.slots.first().player_hero
                        p.save(update_fields=["hero"])
                    else:
                        all_ready = False
                        break

            if all_ready:
                if room.raid:
                    start_structured_raid(room)
                else:
                    # Raid legacy
                    from core.models import Enemy
                    enemy = Enemy.objects.order_by("?").first()
                    if enemy:
                        start_raid(room, enemy=enemy)


def force_close_room(room: RaidRoom):
    """Force close due to timeout: kill all participants' heroes and mark closed.
    Idempotent: safe if called multiple times.
    """
    if room.closed:
        return
    # KO all alive participants and set their PlayerHero HP to 0
    changed_ph_ids = []
    for p in room.participants.select_related("hero").all():
        if p.is_alive:
            p.is_alive = False
            p.save(update_fields=["is_alive"])
        if p.hero_id:
            ph = p.hero
            if ph.current_hp != 0:
                ph.current_hp = 0
                ph.save(update_fields=["current_hp"])
                changed_ph_ids.append(ph.id)
    room.closed = True
    room.state = "finished"
    room.save(update_fields=["closed", "state"])
    RaidDecisionLog.objects.create(
        room=room,
        action_type="finish",
        payload={"winner": "timeout", "closed": True, "affected_player_heroes": changed_ph_ids}
    )
