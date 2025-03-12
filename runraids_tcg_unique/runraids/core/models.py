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
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Coin: {id}'.format(id=self.id)


class MemberCoin(models.Model):
    id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE)
    amount_coin = models.IntegerField()
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Member Coins Owned: {id}'.format(id=self.id)


class Collection(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'ID: {id}'.format(id=self.id)


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
        return 'Card: {id}, {name}'.format(id=self.id, name=self.name_card)


class MemberCollection(models.Model):
    id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Member Collection: {id}'.format(id=self.id)


class CollectionDeck(models.Model):
    id = models.AutoField(primary_key=True)
    collection = models.ForeignKey(Member, on_delete=models.CASCADE)
    deck = models.ForeignKey(Collection, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Collection: {id}, Deck Name: {deck}'.format(id=self.collection_id.id, deck=self.deck_id.name_deck)


class Booster(models.Model):
    id = models.AutoField(primary_key=True)
    name_booster = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}'.format(self.name_booster)


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
