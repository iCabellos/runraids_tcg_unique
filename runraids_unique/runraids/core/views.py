from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from core.forms import MemberLoginForm, CombatActionForm, UpgradeBuildingForm
from core.services.combat_service import calculate_damage
from core.models import (
    Member, PlayerResource, PlayerBuilding, PlayerHero,
    Enemy, Ability, Alliance, AllianceBuilding, AllianceMember, BuildingLevelCost
)
import random


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
                    "image": building.building_type.image.url if building.building_type.image else None,
                })

            context["buildings"] = buildings_info
            context["alliance"] = alliance
            context["role"] = membership.role
        else:
            context["buildings"] = []
            context["alliance"] = None

        return context


# CAMP (Edificios individuales del jugador)
class CampView(TemplateView):
    template_name = "camp.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('member_id'):
            return redirect("index")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member = Member.objects.get(id=self.request.session.get('member_id'))

        heroes_member = PlayerHero.objects.filter(member=member).select_related('hero')
        player_buildings = PlayerBuilding.objects.filter(member=member).select_related("building_type")

        buildings_info = []
        for building in player_buildings:
            next_level = building.level + 1
            costs = BuildingLevelCost.objects.filter(building_type=building.building_type, level=next_level)

            is_max_level = not costs.exists()

            resources = PlayerResource.objects.filter(member=member).select_related("resource_type").order_by(
                "resource_type__name")

            can_upgrade = True

            if not resources:
                can_upgrade = False
            else:
                for cost in costs:
                    res = PlayerResource.objects.filter(member=member, resource_type=cost.resource_type).first()
                    if not res or res.amount < cost.amount:
                        can_upgrade = False
                        break

            buildings_info.append({
                "id": building.id,
                "type": building.building_type.type,
                "name": building.building_type.name,
                "level": building.level,
                "image": building.building_type.image.url if building.building_type.image else None,
                "can_upgrade": can_upgrade,
                "is_max_level": is_max_level,
                "upgrade_costs": list(costs),
                "resources": resources,
            })

        context["member"] = member
        context["buildings"] = buildings_info
        context["upgrade_form"] = UpgradeBuildingForm()
        context["heroes"] = heroes_member
        return context

    def post(self, request, *args, **kwargs):
        member = Member.objects.get(id=self.request.session.get('member_id'))
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


def logout_view(request):
    request.session.flush()
    return redirect("index")
