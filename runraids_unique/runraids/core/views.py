from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from core.forms import MemberLoginForm, CombatActionForm
from core.services.combat_service import calculate_damage
from core.models import Member, PlayerResource, PlayerBuilding, PlayerHero, Enemy, Ability

import random


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


class DashboardView(TemplateView):
    template_name = "dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        member_id = request.session.get('member_id')
        if not member_id:
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

        return context


class CombatView(TemplateView):
    template_name = "combat.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("member_id"):
            return redirect("index")

        member = Member.objects.get(id=request.session["member_id"])
        hero = PlayerHero.objects.filter(member=member).first()

        if not hero:
            return redirect("userprofile")

        # Si no hay estado, inicializamos
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

        # Si es turno del enemigo, procesamos automáticamente y redirigimos
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


class CityView(TemplateView):
    template_name = "city.html"

    def dispatch(self, request, *args, **kwargs):
        member_id = request.session.get('member_id')
        if not member_id:
            return redirect("index")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member_id = self.request.session.get('member_id')
        member = Member.objects.get(id=member_id)

        player_buildings = PlayerBuilding.objects.filter(member=member).select_related("building_type")

        buildings_info = []
        for building in player_buildings:
            buildings_info.append({
                "type": building.building_type.type,
                "name": building.building_type.name,
                "level": building.level,
                "image": building.building_type.image.url if building.building_type.image else None,
                "xp_rate": building.xp_rate if building.building_type.type == 'xp_farming' else None,
                "stored_xp": building.stored_xp if building.building_type.type == 'xp_farming' else None
            })

        context["member"] = member
        context["buildings"] = buildings_info
        return context

def logout_view(request):
    request.session.flush()
    return redirect("index")
