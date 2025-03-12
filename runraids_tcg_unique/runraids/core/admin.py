from django.contrib import admin
from core.models import Member, Coin, MemberCoin, Card, Deck, Collection, CollectionDeck, Attack, Ability, Rarity, \
    MemberCollection, Booster, MemberBooster, Hero, Set


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    pass


@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    pass


@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    pass


@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin):
    pass


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    pass


@admin.register(Booster)
class BoosterAdmin(admin.ModelAdmin):
    pass


@admin.register(MemberBooster)
class MemberBoosterAdmin(admin.ModelAdmin):
    pass


@admin.register(Attack)
class AttackAdmin(admin.ModelAdmin):
    pass


@admin.register(Ability)
class AbilityAdmin(admin.ModelAdmin):
    pass


@admin.register(Rarity)
class RarityAdmin(admin.ModelAdmin):
    pass


@admin.register(MemberCoin)
class MemberCoinAdmin(admin.ModelAdmin):
    pass


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    pass


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    pass


@admin.register(CollectionDeck)
class CollectionDeckAdmin(admin.ModelAdmin):
    pass


@admin.register(MemberCollection)
class MemberCollectionAdmin(admin.ModelAdmin):
    pass
