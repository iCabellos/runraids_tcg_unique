import random

from django.db import models
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now


class Member(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    firstname = models.CharField(max_length=255)
    password_member = models.CharField(max_length=128)
    email = models.EmailField(max_length=255)
    phone = models.IntegerField()
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.password_member.startswith("pbkdf2_sha256$"):
            self.password_member = make_password(self.password_member)
        super().save(*args, **kwargs)

    def __str__(self):
        return 'Member: {id}, {name}'.format(id=self.id, name=self.name)


class Coin(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Coin: {id}, {name}'.format(id=self.id, name=self.name)


class MemberCoin(models.Model):
    id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE)
    amount_coin = models.IntegerField()
    total_amount_coin = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Member Coins Owned: {id_mamber}, {coin}, quantity: {amount}, total: {total}'.format(
            id_mamber=self.member,
            coin=self.coin,
            amount=self.amount_coin, total=self.total_amount_coin)

    def save(self, *args, **kwargs):
        previous_total = MemberCoin.objects.filter(
            member=self.member,
            coin=self.coin
        ).exclude(pk=self.pk).aggregate(models.Sum('amount_coin'))['amount_coin__sum'] or 0

        # Sumar el nuevo amount_coin
        self.total_amount_coin = previous_total + self.amount_coin

        super().save(*args, **kwargs)


class Collection(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Collection ID: {id}'.format(id=self.id)


class Deck(models.Model):
    id = models.AutoField(primary_key=True)
    name_deck = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Deck: {id}, {name}'.format(id=self.id, name=self.name_deck)


class Set(models.Model):
    id = models.AutoField(primary_key=True)
    name_set = models.CharField(max_length=128)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Set: {id}, {name}'.format(id=self.id, name=self.name_set)


class Rarity(models.Model):
    id = models.AutoField(primary_key=True)
    name_rarity = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Rarity: {id}, {name}'.format(id=self.id, name=self.name_rarity)


class Ability(models.Model):
    id = models.AutoField(primary_key=True)
    name_ability = models.CharField(max_length=255)
    description_ability = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Ability: {id}, {name}'.format(id=self.id, name=self.name_ability)


class Hero(models.Model):
    id = models.AutoField(primary_key=True)
    name_hero = models.CharField(max_length=255)
    hp_hero = models.IntegerField()
    description_hero = models.CharField(max_length=255)
    set_hero = models.ForeignKey(Set, on_delete=models.CASCADE)
    rarity_hero = models.ForeignKey(Rarity, on_delete=models.CASCADE)
    ability_hero = models.ForeignKey(Ability, on_delete=models.CASCADE, default=None)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Hero: {id}, {name}'.format(id=self.id, name=self.name_hero)


class Attack(models.Model):
    id = models.AutoField(primary_key=True)
    name_atk = models.CharField(max_length=255)
    description_atk = models.CharField(max_length=255)
    value_atk = models.IntegerField()
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Attack: {id}, {name}'.format(id=self.id, name=self.name_atk)


class Card(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='cards/', default='cards/default.jpg')
    name_card = models.CharField(max_length=255)
    hp_card = models.IntegerField()
    cost_card = models.IntegerField()
    set_card = models.ForeignKey(Set, on_delete=models.CASCADE)
    rarity_card = models.ForeignKey(Rarity, on_delete=models.CASCADE)
    ability_card = models.ForeignKey(Ability, on_delete=models.CASCADE, default=None)
    attack_card = models.ForeignKey(Attack, on_delete=models.CASCADE, default=None)
    description_card = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Card: {id}, {name}, {rarity}'.format(id=self.id, name=self.name_card, rarity=self.rarity_card)


class MemberCollection(models.Model):
    id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Member Collection: {id}'.format(id=self.id)


class CollectionCard(models.Model):
    id = models.AutoField(primary_key=True)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Collection: {id}, Card Name: {deck}'.format(id=self.collection.id, deck=self.card)


class CollectionDeck(models.Model):
    id = models.AutoField(primary_key=True)
    collection = models.ForeignKey(Member, on_delete=models.CASCADE)
    deck = models.ForeignKey(Collection, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Collection: {id}, Deck Name: {deck}'.format(id=self.collection.id, deck=self.deck.name_deck)


class Booster(models.Model):
    id = models.AutoField(primary_key=True)
    set_booster = models.ForeignKey(Set, on_delete=models.CASCADE, null=True)
    name_booster = models.CharField(max_length=255)
    quantity_of_cards = models.IntegerField(blank=False, null=False, default=1)
    cost = models.IntegerField(blank=True, null=False, default=0)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}'.format(self.name_booster)

    def open_booster(self, set, member):
        money = MemberCoin.objects.filter(member=member, coin=2).last()
        if money.total_amount_coin >= self.cost:
            new_total_amount = MemberCoin()
            new_total_amount.member = Member.objects.filter(id=member).last()
            new_total_amount.coin = Coin.objects.filter(id=2).last()
            new_total_amount.amount_coin = self.cost
            new_total_amount.save()

            member_logged = Member.objects.filter(id=member).first()
            if not member_logged:
                return None

            member_collection = MemberCollection.objects.filter(member=member_logged).first()

            if not member_collection:
                new_collection = Collection.objects.create()
                new_member_collection = MemberCollection.objects.create(member=member_logged, collection=new_collection)
                member_collection = new_member_collection

            collection = member_collection.collection
            all_cards_list = Card.objects.filter(set_card=set)

            cards_opened = []

            for i in range(self.quantity_of_cards):
                if i == 2 and random.randint(1, 100) <= 2:
                    epic_cards = all_cards_list.filter(rarity_card=3)
                    if epic_cards.exists():
                        random_card = random.choice(list(epic_cards))
                else:
                    rare_cards = all_cards_list.filter(rarity_card=2) if i == 2 else all_cards_list.filter(
                        rarity_card=1)
                    if rare_cards.exists():
                        random_card = random.choice(list(rare_cards))

                if random_card:
                    CollectionCard.objects.create(collection=collection, card=random_card)
                    cards_opened.append(random_card)

            return {
                'ok': True,
                'cards': cards_opened
            }
        else:
            return {
                'ok': False,
                'cards': []
            }


class MemberBooster(models.Model):
    id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    booster = models.ForeignKey(Booster, on_delete=models.CASCADE)
    piti_booster = models.IntegerField()
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Member: {member}, Piti: {piti}, Booster: {booster}'.format(member=self.member,
                                                                           piti=self.piti_booster,
                                                                           booster=self.booster)
