import json
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import TemplateView
from core.forms import MemberLoginForm
from core.models import Member, Booster, MemberCollection, CollectionCard, MemberCoin


def boosters_to_template() -> list:
    new_boosters = []
    boosters = Booster.objects.all()
    for booster in boosters:
        new_booster = booster
        new_booster.cost = -new_booster.cost
        new_boosters.append(new_booster)

    return new_boosters


def get_aurum_coin_from_member(member_id: int) -> int:
    member_coins = MemberCoin.objects.filter(member=member_id, coin=1)
    return member_coins.last().total_amount_coin


def get_argentum_coin_from_member(member_id: int) -> int:
    member_coins = MemberCoin.objects.filter(member=member_id, coin=2)
    return member_coins.last().total_amount_coin


def get_coins_from_member(member_id: int) -> list:
    au = get_aurum_coin_from_member(member_id=member_id)
    ar = get_argentum_coin_from_member(member_id=member_id)
    return [au, ar]


def get_cards_from_member_collection(member_id: int) -> list:
    collections = MemberCollection.objects.filter(member=member_id)
    cards = [
        list_card.card
        for collection in collections
        for list_card in CollectionCard.objects.filter(collection=collection.id)
    ]
    return cards


def order_cards_by_id(cards: list) -> list:
    unique_cards = {}

    for card in sorted(cards, key=lambda c: c.id):
        if card.id not in unique_cards:
            unique_cards[card.id] = {
                'card': card,
                'dupes': 1
            }
        else:
            unique_cards[card.id]['dupes'] += 1

    return list(unique_cards.values())


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
            member = Member.objects.get(phone=phone)

            request.session['member_id'] = member.id
            return redirect("userprofile")

        return render(request, self.template_name, {'form': form})


class DashboardView(TemplateView):
    template_name = "dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('member_id'):
            return redirect("index")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member_id = self.request.session.get('member_id')
        context.update({
            'member': Member.objects.get(id=member_id),
        })
        return context


class CollectionView(TemplateView):
    template_name = "member_collection.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('member_id'):
            return redirect("index")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member_id = self.request.session.get('member_id')
        context.update({
            'cards_collection': order_cards_by_id(get_cards_from_member_collection(member_id)),
            'member': Member.objects.get(id=member_id),
        })
        return context


class ShopView(TemplateView):
    template_name = "shop.html"

    def post(self, request):
        member = request.session.get('member_id')
        if not member:
            return redirect("index")

        booster_id = request.POST.get("booster_id")
        booster = get_object_or_404(Booster, id=booster_id)
        opened = booster.open_booster(booster.set_booster, member)
        opened_cards = opened["cards"] if opened["ok"] else []

        serialized_cards = json.dumps([
            {
                'id': card.id,
                'name_card': card.name_card,
                'hp_card': card.hp_card,
                'cost_card': card.cost_card,
                'description_card': card.description_card,
                'image': {'url': card.image.url},
                'rarity_card': {'id': card.rarity_card.id},
                'ability_card': {
                    'id': card.ability_card.id,
                    'name_ability': card.ability_card.name_ability,
                    'description_ability': card.ability_card.description_ability,
                },
                'attack_card': {
                    'id': card.attack_card.id,
                    'name_atk': card.attack_card.name_atk,
                    'description_atk': card.attack_card.description_atk,
                },
            }
            for card in opened_cards
        ], cls=DjangoJSONEncoder)

        return render(request, self.template_name, {
            'member': Member.objects.get(id=member),
            'boosters': boosters_to_template(),
            'opened_cards_json': serialized_cards,
            'au': get_aurum_coin_from_member(member_id=member),
            'ar': get_argentum_coin_from_member(member_id=member),
            'booster_opened': True
        })

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('member_id'):
            return redirect("index")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member_id = self.request.session.get('member_id')
        context.update({
            'cards_collection': order_cards_by_id(get_cards_from_member_collection(member_id)),
            'member': Member.objects.get(id=member_id),
            'boosters': boosters_to_template(),
            'au': get_aurum_coin_from_member(member_id=member_id),
            'ar': get_argentum_coin_from_member(member_id=member_id),
            'booster_opened': False,
        })
        return context


def logout_view(request):
    request.session.flush()
    return redirect("index")
