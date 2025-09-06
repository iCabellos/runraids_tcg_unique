from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.utils.timezone import now as tz_now
from core.forms import MemberLoginForm, CombatActionForm, UpgradeBuildingForm
from core.services.combat_service import calculate_damage
from core.models import (
    Member, PlayerResource, PlayerBuilding, PlayerHero,
    Enemy, Ability, Alliance, AllianceBuilding, AllianceMember, BuildingLevelCost, ResourceType,
    Banner
)
import random


def get_member_or_redirect(request):
    """
    Obtiene el member de la sesión o retorna None si no existe.
    Si no existe, limpia la sesión.
    """
    member_id = request.session.get('member_id')
    if not member_id:
        return None

    try:
        return Member.objects.get(id=member_id)
    except Member.DoesNotExist:
        request.session.flush()
        return None


class MemberRequiredMixin:
    """Mixin que requiere que el usuario esté autenticado como member"""

    def dispatch(self, request, *args, **kwargs):
        member = get_member_or_redirect(request)
        if not member:
            return redirect("index")
        return super().dispatch(request, *args, **kwargs)


# INDEX
class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MemberLoginForm()
        return context

    def post(self, request):
        form = MemberLoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            try:
                member = Member.objects.get(phone=phone)
                request.session['member_id'] = member.id
                return redirect("userprofile")
            except Member.DoesNotExist:
                form.add_error(None, "Teléfono no registrado")

        return render(request, self.template_name, {'form': form})


# DASHBOARD
class DashboardView(TemplateView):
    template_name = "dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('member_id'):
            return redirect("index")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member_id = self.request.session.get('member_id')
        member = Member.objects.get(id=member_id)

        context['member'] = member
        context['resources'] = PlayerResource.objects.filter(member=member)
        context['buildings'] = PlayerBuilding.objects.filter(member=member)
        context['heroes'] = PlayerHero.objects.filter(member=member)

        # Alianza
        alliance_membership = AllianceMember.objects.filter(member=member).select_related('alliance').first()
        if alliance_membership:
            context['alliance'] = alliance_membership.alliance
            context['alliance_role'] = alliance_membership.role
            context['alliance_buildings'] = AllianceBuilding.objects.filter(alliance=alliance_membership.alliance)

        return context


# CITY (Edificios de alianza)
class CityView(TemplateView):
    template_name = "city.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('member_id'):
            return redirect("index")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member = Member.objects.get(id=self.request.session["member_id"])

        membership = AllianceMember.objects.filter(member=member).first()
        if membership:
            alliance = membership.alliance
            buildings = AllianceBuilding.objects.filter(alliance=alliance).select_related("building_type")

            buildings_info = []
            for building in buildings:
                buildings_info.append({
                    "type": building.building_type.type,
                    "name": building.building_type.name,
                    "level": building.level,
                    "image": building.building_type.get_image_url(),
                })

            context["buildings"] = buildings_info
            context["alliance"] = alliance
            context["role"] = membership.role
        else:
            context["buildings"] = []
            context["alliance"] = None

        return context


# CAMP (Edificios individuales del jugador)
class CampView(MemberRequiredMixin, TemplateView):
    template_name = "camp.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member = get_member_or_redirect(self.request)

        heroes_member = PlayerHero.objects.filter(member=member).select_related('hero')
        player_buildings = (
            PlayerBuilding.objects
            .filter(member=member)
            .select_related("building_type")
        )

        # 🔹 Cargamos todos los tipos de recursos definidos en la DB
        all_resource_types = ResourceType.objects.all().order_by("id")

        # Recursos del jugador en dict {resource_type_id: amount}
        player_res = {
            pr.resource_type_id: pr.amount
            for pr in PlayerResource.objects.filter(member=member)
        }

        # Construimos lista completa (si no hay, amount=0)
        resources_info = []
        for rt in all_resource_types:
            resources_info.append({
                "id": rt.id,
                "name": rt.name,
                "image": rt.get_image_url(),
                "amount": player_res.get(rt.id, 0),
            })

        buildings_info = []
        for building in player_buildings:
            next_level = building.level + 1
            costs = BuildingLevelCost.objects.filter(
                building_type=building.building_type, level=next_level
            )
            is_max_level = not costs.exists()

            can_upgrade = True
            if is_max_level:
                can_upgrade = False
            else:
                for cost in costs:
                    if player_res.get(cost.resource_type_id, 0) < cost.amount:
                        can_upgrade = False
                        break

            buildings_info.append({
                "id": building.id,
                "type": building.building_type.type,
                "name": building.building_type.name,
                "level": building.level,
                "image": building.building_type.get_image_url(),
                "can_upgrade": can_upgrade,
                "is_max_level": is_max_level,
                "upgrade_costs": list(costs),
            })

        context.update({
            "member": member,
            "buildings": buildings_info,
            "upgrade_form": UpgradeBuildingForm(),
            "heroes": heroes_member,
            "resources": resources_info,  # 🔹 lista siempre completa (Oro, Madera, Elixir…)
        })
        return context

    def post(self, request, *args, **kwargs):
        member = get_member_or_redirect(self.request)
        if not member:
            return redirect("index")
        form = UpgradeBuildingForm(request.POST, member=member)
        if form.is_valid():
            form.save()
        return redirect("camp")


# COMBATE
class CombatView(TemplateView):
    template_name = "combat.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("member_id"):
            return redirect("index")

        member = Member.objects.get(id=request.session["member_id"])
        hero = PlayerHero.objects.filter(member=member).first()

        if not hero:
            return redirect("userprofile")

        if "combat" not in request.session:
            enemy = Enemy.objects.order_by("?").first()
            hero_hp = hero.current_hp
            enemy_hp = enemy.base_hp
            turn = "hero" if hero.get_speed() >= enemy.speed else "enemy"
            log = [f"¡Combate iniciado contra {enemy.name}!"]

            request.session["combat"] = {
                "enemy_id": enemy.id,
                "hero_hp": hero_hp,
                "enemy_hp": enemy_hp,
                "turn": turn,
                "log": log
            }

        state = request.session["combat"]
        if state["turn"] == "enemy":
            enemy = Enemy.objects.get(id=state["enemy_id"])
            ability = random.choice(enemy.abilities.all())
            dmg = calculate_damage(enemy.attack, ability.power, hero.get_defense())
            state["hero_hp"] -= dmg
            state["log"].append(f"{enemy.name} usa {ability.name} y hace {dmg} de daño a {hero.hero.name}.")

            if state["hero_hp"] <= 0:
                state["log"].append("¡Perdiste!")
                request.session.pop("combat")
            else:
                state["turn"] = "hero"
                request.session["combat"] = state

            return redirect("combat")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member = Member.objects.get(id=self.request.session["member_id"])
        hero = PlayerHero.objects.filter(member=member).first()
        state = self.request.session["combat"]
        enemy = Enemy.objects.get(id=state["enemy_id"])
        resources = PlayerResource.objects.filter(member=member)

        form = CombatActionForm(hero=hero)

        context.update({
            "member": member,
            "hero": hero,
            "enemy": enemy,
            "form": form,
            "log": state["log"],
            "hero_hp": state["hero_hp"],
            "enemy_hp": state["enemy_hp"],
            "turn": state["turn"],
            "resources": resources,
        })
        return context

    def post(self, request, *args, **kwargs):
        member = Member.objects.get(id=request.session["member_id"])
        hero = PlayerHero.objects.filter(member=member).first()
        state = request.session.get("combat")

        if not hero or not state:
            return redirect("combat")

        enemy = Enemy.objects.get(id=state["enemy_id"])
        form = CombatActionForm(request.POST, hero=hero)

        if form.is_valid():
            ability_id = int(form.cleaned_data["ability_id"])
            ability = Ability.objects.get(id=ability_id)

            dmg = calculate_damage(hero.get_attack(), ability.power, enemy.defense)
            state["enemy_hp"] -= dmg
            state["log"].append(f"{hero.hero.name} usa {ability.name} y hace {dmg} de daño a {enemy.name}.")

            if state["enemy_hp"] <= 0:
                state["log"].append("¡Ganaste!")
                request.session.pop("combat")
            else:
                state["turn"] = "enemy"
                request.session["combat"] = state

        return redirect("combat")

from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.utils.timezone import now as tz_now
from core.models import Member, PlayerResource, Banner

class BannerView(TemplateView):
    template_name = "bathroom.html"


class RaidRoomPage(TemplateView):
    template_name = "raid_room.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('member_id'):
            return redirect("index")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        member = Member.objects.get(id=self.request.session.get('member_id'))

        # Heroes del jugador (para elegir equipo/líder)
        heroes_member = PlayerHero.objects.filter(member=member).select_related('hero').order_by('id')
        ctx['my_heroes_data'] = [
            {
                "id": ph.id,
                "name": ph.hero.name,
                "hp": ph.current_hp,
                "max_hp": ph.s_hp(),
                "base_hero_id": ph.hero_id,
                "image": ph.hero.get_image_url(),
            }
            for ph in heroes_member
        ]

        # Usamos Enemy como 'tipo de raid' seleccionable en modo Solo
        enemies = Enemy.objects.all().order_by('id')
        ctx['available_raids_data'] = [
            {"id": e.id, "name": e.name}
            for e in enemies
        ]

        # Información de banners (ya existente en la página, opcional)
        banners_qs = (
            Banner.objects.filter(is_active=True)
            .prefetch_related(
                "entries__hero__rarity",
                "rewards__items__resource_type",
                "cost_resource",
            )
            .order_by("-created_at")
        )

        banners_info = []
        now_ = tz_now()
        for b in banners_qs:
            if b.starts_at and now_ < b.starts_at:
                continue
            if b.ends_at and now_ > b.ends_at:
                continue

            pr = PlayerResource.objects.filter(member=member, resource_type=b.cost_resource).first()
            balance = pr.amount if pr else 0
            can_afford = balance >= b.cost_amount

            promo_entries, normal_entries, rewards = [], [], []

            for e in b.entries.all():
                item = {
                    "hero_id": e.hero_id,
                    "name": e.hero.name,
                    "codename": e.hero.codename,
                    "rarity": e.hero.rarity.type if e.hero.rarity else "common",
                    "image": e.hero.get_image_url(),
                    "is_promotional": e.is_promotional,
                }
                (promo_entries if e.is_promotional else normal_entries).append(item)

            for r in b.rewards.all():
                items = [{"resource_name": it.resource_type.name, "min": it.min_amount, "max": it.max_amount}
                         for it in r.items.all()]
                rewards.append({"name": r.name or "Recompensa", "items": items})

            banners_info.append({
                "id": b.id,
                "name": b.name,
                "description": b.description,
                "image": getattr(b, 'image', None) and b.image.url,  # Banner images are actual uploads
                "cost": {
                    "resource_name": b.cost_resource.name,
                    "resource_image": b.cost_resource.get_image_url(),
                    "amount": b.cost_amount,
                    "balance": balance,
                    "can_afford": can_afford,
                },
                "rates": {
                    "promo_rate": b.promo_rate,
                    "normal_rate": b.normal_rate,
                    "other_rate": max(0.0, 1.0 - (b.promo_rate + b.normal_rate)),
                },
                "promo_entries": promo_entries,
                "normal_entries": normal_entries,
                "rewards": rewards,
            })

        ctx["member"] = member
        ctx["banners"] = banners_info
        return ctx


class MatchmakingView(MemberRequiredMixin, TemplateView):
    template_name = "matchmaking.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        member = get_member_or_redirect(self.request)

        # Obtener equipo activo del jugador
        from core.models import Team, Raid
        team = Team.objects.filter(owner=member, is_active=True).prefetch_related('slots__player_hero__hero').first()

        # Obtener raids disponibles
        available_raids = Raid.objects.all().order_by('difficulty', 'name')

        ctx["member"] = member
        ctx["team"] = team
        ctx["available_raids"] = available_raids
        return ctx


class MatchmakingRoomView(MemberRequiredMixin, TemplateView):
    template_name = "matchmaking_room.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        member = get_member_or_redirect(self.request)
        room_id = kwargs.get('room_id')

        try:
            from core.models import RaidRoom
            room = RaidRoom.objects.get(pk=room_id)
            ctx["room"] = room
            ctx["member"] = member
            ctx["is_owner"] = room.owner_id == member.id
        except RaidRoom.DoesNotExist:
            ctx["error"] = "Sala de matchmaking no encontrada"

        return ctx


class RaidRoomDetailView(MemberRequiredMixin, TemplateView):
    template_name = "raid_room_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        member = get_member_or_redirect(self.request)
        room_id = kwargs.get('room_id')

        try:
            from core.models import RaidRoom
            room = RaidRoom.objects.get(pk=room_id)
            ctx["room"] = room
            ctx["member"] = member
        except RaidRoom.DoesNotExist:
            ctx["error"] = "Sala de raid no encontrada"

        return ctx


from django.views.decorators.http import require_POST
from django.http import JsonResponse
from core.services.pulls import perform_pull, PullError, InsufficientCurrency
from core.services.raid_service import matchmaking_join, process_tick, submit_player_decision, RaidError, start_solo_raid
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import models

@require_POST
def api_pull(request, banner_id):
    """Tirada x1: devuelve JSON con el resultado."""
    member_id = request.session.get('member_id')
    if not member_id:
        return JsonResponse({"ok": False, "error": "unauthorized"}, status=401)

    try:
        member = Member.objects.get(pk=member_id)
        banner = Banner.objects.get(pk=banner_id, is_active=True)
    except (Member.DoesNotExist, Banner.DoesNotExist):
        return JsonResponse({"ok": False, "error": "not_found"}, status=404)

    try:
        result = perform_pull(member, banner)
        return JsonResponse({"ok": True, "result": result})
    except InsufficientCurrency as e:
        return JsonResponse({"ok": False, "error": "insufficient_funds", "detail": str(e)}, status=400)
    except PullError as e:
        return JsonResponse({"ok": False, "error": "pull_error", "detail": str(e)}, status=400)


@require_POST
def api_pull_multi(request, banner_id):
    """Tirada múltiple x10 (o usa 'count' si lo envías en el form). Responde JSON con array de resultados."""
    member_id = request.session.get('member_id')
    if not member_id:
        return JsonResponse({"ok": False, "error": "unauthorized"}, status=401)

    try:
        member = Member.objects.get(pk=member_id)
        banner = Banner.objects.get(pk=banner_id, is_active=True)
    except (Member.DoesNotExist, Banner.DoesNotExist):
        return JsonResponse({"ok": False, "error": "not_found"}, status=404)

    # si llega 'count' del form, lo usamos; por defecto 10
    try:
        count = int(request.POST.get("count", "10"))
    except ValueError:
        count = 10
    count = max(1, min(count, 10))

    results = []
    try:
        for _ in range(count):
            results.append(perform_pull(member, banner))
        return JsonResponse({"ok": True, "results": results, "count": count})
    except InsufficientCurrency as e:
        return JsonResponse({"ok": False, "error": "insufficient_funds", "detail": str(e)}, status=400)
    except PullError as e:
        return JsonResponse({"ok": False, "error": "pull_error", "detail": str(e)}, status=400)

def logout_view(request):
    request.session.flush()
    return redirect("index")


# =============== API RAIDS ===============
@csrf_exempt
@require_POST
def api_raid_matchmaking_join(request):
    member_id = request.session.get('member_id')
    if not member_id:
        return JsonResponse({"ok": False, "error": "unauthorized"}, status=401)

    from core.models import Member, Raid, Team
    member = Member.objects.get(pk=member_id)

    raid_id = request.POST.get('raid_id')
    team_id = request.POST.get('team_id')

    if not raid_id:
        return JsonResponse({"ok": False, "error": "raid_id_required"}, status=400)

    try:
        raid = Raid.objects.get(pk=int(raid_id))
    except Raid.DoesNotExist:
        return JsonResponse({"ok": False, "error": "raid_not_found"}, status=404)

    team = None
    if team_id:
        try:
            team = Team.objects.get(pk=int(team_id), owner=member)
        except Team.DoesNotExist:
            return JsonResponse({"ok": False, "error": "team_not_found"}, status=404)

    try:
        room = matchmaking_join(member, raid=raid, team=team)
        return JsonResponse({"ok": True, "room_id": room.id})
    except RaidError as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_raid_start(request, room_id):
    """Iniciar raid manualmente (solo el owner puede hacerlo)"""
    try:
        from core.models import RaidRoom
        member = get_member_or_redirect(request)
        if not member:
            return JsonResponse({"ok": False, "error": "No autenticado"}, status=401)
        room = RaidRoom.objects.get(pk=room_id)

        # Verificar que sea el owner
        if room.owner_id != member.id:
            return JsonResponse({"ok": False, "error": "Solo el líder puede iniciar la raid"}, status=403)

        # Verificar que la sala esté en estado ready
        if room.state not in ["ready", "waiting"]:
            return JsonResponse({"ok": False, "error": "La sala no está lista para iniciar"}, status=400)

        # Iniciar la raid
        if room.raid:
            from core.services.raid_service import start_structured_raid
            start_structured_raid(room)
        else:
            from core.services.raid_service import start_raid
            from core.models import Enemy
            enemy = Enemy.objects.order_by("?").first()
            if enemy:
                start_raid(room, enemy=enemy)

        return JsonResponse({"ok": True})
    except (Member.DoesNotExist, RaidRoom.DoesNotExist):
        return JsonResponse({"ok": False, "error": "Sala no encontrada"}, status=404)
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)


def _serialize_room(room):
    # tick on read (asíncrono simple)
    process_tick(room)
    from core.models import RaidParticipant, RaidEnemyInstance, RaidTurn, RaidDecisionLog, Team

    # Obtener participantes con sus equipos completos
    parts = list(room.participants.select_related('member', 'hero__hero').all())
    enemies = list(room.enemies.select_related('enemy').all())
    turn = room.turns.filter(resolved=False).order_by('index').first()
    logs = list(room.decision_logs.order_by('-created_at')[:30])

    # Serializar participantes con equipos completos
    participants_data = []
    for p in parts:
        # Obtener equipo completo del jugador
        team = Team.objects.filter(owner=p.member, is_active=True).prefetch_related('slots__player_hero__hero').first()
        team_heroes = []

        if team:
            for slot in team.slots.all():
                ph = slot.player_hero
                team_heroes.append({
                    "id": ph.id,
                    "name": ph.hero.name,
                    "image": ph.hero.get_image_url(),
                    "current_hp": ph.current_hp,
                    "max_hp": ph.s_hp(),
                    "is_alive": ph.current_hp > 0,
                    "position": slot.position,
                })

        participants_data.append({
            "member_id": p.member_id,
            "member_name": p.member.name,
            "is_alive": p.is_alive,
            "is_ready": p.is_ready,
            "player_color": p.player_color,
            "team_heroes": team_heroes,
            # Héroe principal (para compatibilidad)
            "hero": p.hero.hero.name if p.hero else None,
            "hero_hp": p.hero.current_hp if p.hero else None,
        })

    # Información de la raid y oleada actual
    raid_info = None
    if room.raid:
        current_wave = None
        try:
            current_wave = room.raid.waves.get(wave_number=room.wave_index + 1)
        except:
            pass

        raid_info = {
            "id": room.raid.id,
            "name": room.raid.name,
            "difficulty": room.raid.difficulty,
            "current_wave": room.wave_index + 1 if current_wave else None,
            "wave_name": current_wave.name if current_wave else None,
            "total_waves": room.raid.waves.count(),
        }

    return {
        "room_id": room.id,
        "name": room.name,
        "state": room.state,
        "max_players": room.max_players,
        "raid": raid_info,
        "participants": participants_data,
        "enemies": [
            {
                "id": e.id,
                "name": e.enemy.name,
                "image": e.enemy.get_image_url(),
                "hp": e.current_hp,
                "max_hp": e.max_hp,
                "alive": e.is_alive,
                "speed": e.speed,
            } for e in enemies
        ],
        "turn": None if not turn else {
            "index": turn.index,
            "actor_type": turn.actor_type,
            "member_id": turn.participant.member_id if turn.participant_id else None,
            "enemy_id": turn.enemy_instance_id,
            "hero_id": turn.hero_instance.id if turn.hero_instance else None,
            "hero_name": turn.hero_instance.hero.name if turn.hero_instance else (turn.participant.hero.hero.name if turn.participant and turn.participant.hero else None),
            "hero_speed": turn.hero_instance.s_speed() if turn.hero_instance else (turn.participant.hero.s_speed() if turn.participant and turn.participant.hero else None),
        },
        "logs": [
            {
                "ts": l.created_at.isoformat(),
                "action": l.action_type,
                "actor": l.actor,
                "payload": l.payload,
                "member_id": l.participant.member_id if l.participant_id else None,
            } for l in logs[::-1]
        ]
    }


from django.views.decorators.http import require_GET
@require_GET
def api_raid_state(request, room_id):
    from core.models import RaidRoom
    try:
        room = RaidRoom.objects.get(pk=room_id)
    except RaidRoom.DoesNotExist:
        return JsonResponse({"ok": False, "error": "not_found"}, status=404)
    data = _serialize_room(room)
    return JsonResponse({"ok": True, "state": data})


@csrf_exempt
@require_POST
def api_raid_solo_start(request):
    member_id = request.session.get('member_id')
    if not member_id:
        return JsonResponse({"ok": False, "error": "unauthorized"}, status=401)

    from core.models import Member, Raid, Team, Enemy
    member = Member.objects.get(pk=member_id)

    raid_id = request.POST.get('raid_id')
    team_id = request.POST.get('team_id')
    enemy_id = request.POST.get('raid_type_id')  # Legacy support

    try:
        if raid_id:
            # Nueva raid estructurada
            raid = Raid.objects.get(pk=int(raid_id))
            team = None
            if team_id:
                team = Team.objects.get(pk=int(team_id), owner=member)
            room = start_solo_raid(member, raid=raid, team=team)
        elif enemy_id:
            # Raid legacy con enemigo simple
            enemy = Enemy.objects.get(pk=int(enemy_id))
            team = Team.objects.filter(owner=member, is_active=True).first()
            room = start_solo_raid(member, enemy=enemy, team=team)
        else:
            return JsonResponse({"ok": False, "error": "missing_params"}, status=400)

        return JsonResponse({"ok": True, "room_id": room.id})
    except (Raid.DoesNotExist, Enemy.DoesNotExist, Team.DoesNotExist):
        return JsonResponse({"ok": False, "error": "resource_not_found"}, status=404)
    except RaidError as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)


@csrf_exempt
@require_POST
def api_raid_decision(request):
    member_id = request.session.get('member_id')
    if not member_id:
        return JsonResponse({"ok": False, "error": "unauthorized"}, status=401)
    from core.models import Member, RaidRoom
    member = Member.objects.get(pk=member_id)
    room_id = request.POST.get('room_id')
    try:
        room = RaidRoom.objects.get(pk=room_id)
    except RaidRoom.DoesNotExist:
        return JsonResponse({"ok": False, "error": "not_found"}, status=404)
    target_enemy_id = request.POST.get('target_enemy_id')
    try:
        submit_player_decision(member, room, ability_id=None, target_enemy_id=int(target_enemy_id) if target_enemy_id else None)
        return JsonResponse({"ok": True})
    except RaidError as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)


@csrf_exempt
@require_POST
def api_hero_heal(request):
    """Cura un PlayerHero del miembro autenticado al máximo HP escalado (s_hp)."""
    member_id = request.session.get('member_id')
    if not member_id:
        return JsonResponse({"ok": False, "error": "unauthorized"}, status=401)
    from core.models import Member, PlayerHero
    member = Member.objects.get(pk=member_id)
    hero_id = request.POST.get('player_hero_id')
    if not hero_id:
        return JsonResponse({"ok": False, "error": "missing_player_hero_id"}, status=400)
    ph = PlayerHero.objects.filter(pk=int(hero_id), member=member).select_related('hero').first()
    if not ph:
        return JsonResponse({"ok": False, "error": "not_found"}, status=404)
    max_hp = ph.s_hp()
    ph.current_hp = max_hp
    ph.save(update_fields=["current_hp"])
    return JsonResponse({"ok": True, "player_hero_id": ph.id, "current_hp": ph.current_hp, "max_hp": max_hp})


@csrf_exempt
@require_POST
def api_hero_heal_all(request):
    """Cura todos los PlayerHero del miembro autenticado al máximo HP."""
    member_id = request.session.get('member_id')
    if not member_id:
        return JsonResponse({"ok": False, "error": "unauthorized"}, status=401)

    try:
        from core.models import Member, PlayerHero
        member = Member.objects.get(pk=member_id)
        heroes = PlayerHero.objects.filter(member=member).select_related('hero')

        healed_count = 0
        for hero in heroes:
            max_hp = hero.s_hp()
            if hero.current_hp < max_hp:
                hero.current_hp = max_hp
                hero.save(update_fields=["current_hp"])
                healed_count += 1

        return JsonResponse({
            "ok": True,
            "healed_count": healed_count,
            "total_heroes": heroes.count()
        })
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)


# ====== TEAM MANAGEMENT API ======
from django.views.decorators.http import require_GET
from core.models import Team, TeamSlot

@require_GET
def api_team_get(request):
    member_id = request.session.get('member_id')
    if not member_id:
        return JsonResponse({"ok": False, "error": "unauthorized"}, status=401)
    member = Member.objects.get(pk=member_id)
    team = Team.objects.filter(owner=member, is_active=True).first()

    def ph_info(ph: PlayerHero):
        return {
            "id": ph.id,
            "name": ph.hero.name,
            "hp": ph.current_hp,
            "max_hp": ph.s_hp(),
            "base_hero_id": ph.hero_id,
            "image": ph.hero.get_image_url(),
        }

    heroes_qs = PlayerHero.objects.filter(member=member).select_related('hero').order_by('id')
    heroes = [ph_info(ph) for ph in heroes_qs]

    team_payload = None
    if team:
        slots = list(team.slots.select_related('player_hero__hero').order_by('position'))
        team_payload = {
            "id": team.id,
            "name": team.name,
            "slots": [ph_info(s.player_hero) | {"slot_id": s.id, "position": s.position} for s in slots]
        }
    return JsonResponse({"ok": True, "team": team_payload, "heroes": heroes})


@csrf_exempt
@require_POST
def api_team_create(request):
    member_id = request.session.get('member_id')
    if not member_id:
        return JsonResponse({"ok": False, "error": "unauthorized"}, status=401)
    member = Member.objects.get(pk=member_id)
    team = Team.objects.filter(owner=member, is_active=True).first()
    if not team:
        team = Team.objects.create(owner=member, name=(request.POST.get('name') or 'Equipo'), is_active=True)
    return JsonResponse({"ok": True, "team_id": team.id})


@csrf_exempt
@require_POST
def api_team_add(request):
    member_id = request.session.get('member_id')
    if not member_id:
        return JsonResponse({"ok": False, "error": "unauthorized"}, status=401)
    member = Member.objects.get(pk=member_id)
    ph_id = request.POST.get('player_hero_id')
    if not ph_id:
        return JsonResponse({"ok": False, "error": "missing_player_hero_id"}, status=400)
    ph = PlayerHero.objects.filter(pk=int(ph_id), member=member).select_related('hero').first()
    if not ph:
        return JsonResponse({"ok": False, "error": "not_found"}, status=404)
    team = Team.objects.filter(owner=member, is_active=True).first() or Team.objects.create(owner=member, is_active=True)
    # validations
    slots_qs = team.slots.select_related('player_hero__hero')
    if slots_qs.count() >= 4:
        return JsonResponse({"ok": False, "error": "team_full"}, status=400)
    base_ids = set(slots_qs.values_list('player_hero__hero_id', flat=True))
    if ph.hero_id in base_ids:
        return JsonResponse({"ok": False, "error": "duplicate_hero"}, status=400)
    pos = (slots_qs.aggregate(m=models.Max('position')).get('m') or 0) + 1
    slot = TeamSlot.objects.create(team=team, player_hero=ph, position=pos)
    return JsonResponse({"ok": True, "slot_id": slot.id, "team_id": team.id})


@csrf_exempt
@require_POST
def api_team_remove(request):
    member_id = request.session.get('member_id')
    if not member_id:
        return JsonResponse({"ok": False, "error": "unauthorized"}, status=401)
    member = Member.objects.get(pk=member_id)
    ph_id = request.POST.get('player_hero_id')
    team = Team.objects.filter(owner=member, is_active=True).first()
    if not team:
        return JsonResponse({"ok": True})
    if ph_id:
        TeamSlot.objects.filter(team=team, player_hero_id=int(ph_id)).delete()
    return JsonResponse({"ok": True})


# ====== RAID MANAGEMENT API ======
@require_GET
def api_raids_available(request):
    """Obtener raids disponibles"""
    from core.models import Raid
    raids = Raid.objects.all().order_by('difficulty', 'name')
    raids_data = []
    for raid in raids:
        raids_data.append({
            "id": raid.id,
            "name": raid.name,
            "description": raid.description,
            "difficulty": raid.difficulty,
            "difficulty_display": raid.get_difficulty_display(),
            "min_players": raid.min_players,
            "max_players": raid.max_players,
            "image": getattr(raid, 'image', None) and raid.image.url,  # Raid images are actual uploads
        })
    return JsonResponse({"ok": True, "raids": raids_data})


@require_GET
def api_raid_rooms_available(request):
    """Obtener salas de raid disponibles para matchmaking"""
    from core.models import RaidRoom
    rooms = RaidRoom.objects.filter(state="waiting").select_related('raid', 'owner').order_by('created_at')
    rooms_data = []
    for room in rooms:
        current_players = room.participants.count()
        rooms_data.append({
            "id": room.id,
            "name": room.name,
            "raid": {
                "id": room.raid.id if room.raid else None,
                "name": room.raid.name if room.raid else "Raid Simple",
                "difficulty": room.raid.difficulty if room.raid else "normal",
            },
            "owner": room.owner.name if room.owner else "Sistema",
            "current_players": current_players,
            "max_players": room.max_players,
            "can_join": current_players < room.max_players,
        })
    return JsonResponse({"ok": True, "rooms": rooms_data})


@csrf_exempt
@require_POST
def api_team_update(request):
    """Actualizar equipo completo"""
    member_id = request.session.get('member_id')
    if not member_id:
        return JsonResponse({"ok": False, "error": "unauthorized"}, status=401)

    member = Member.objects.get(pk=member_id)
    team = Team.objects.filter(owner=member, is_active=True).first()

    if not team:
        return JsonResponse({"ok": False, "error": "no_active_team"}, status=404)

    # Limpiar slots existentes
    team.slots.all().delete()

    # Añadir nuevos héroes
    hero_ids = request.POST.getlist('hero_ids[]')
    if not hero_ids:
        hero_ids = [request.POST.get('hero_ids')] if request.POST.get('hero_ids') else []

    for i, hero_id in enumerate(hero_ids[:4]):  # Máximo 4 héroes
        try:
            player_hero = PlayerHero.objects.get(pk=int(hero_id), member=member)
            TeamSlot.objects.create(team=team, player_hero=player_hero, position=i)
        except (PlayerHero.DoesNotExist, ValueError):
            continue

    return JsonResponse({"ok": True, "team_id": team.id})
