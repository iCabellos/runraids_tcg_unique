from core.models import PlayerHero, Enemy, Ability


class SimpleCombatResult:
    def __init__(self, winner, log):
        self.winner = winner
        self.log = log


def calculate_damage(attack_stat, ability_power, defense_stat):
    raw = (attack_stat * ability_power) / 100
    dmg = raw - (defense_stat * 0.15)
    return max(0, int(dmg))


def simulate_combat_with_ability(hero: PlayerHero, enemy: Enemy, ability_id: int) -> SimpleCombatResult:
    log = []
    ability = Ability.objects.get(id=ability_id)

    hero_hp = hero.current_hp
    enemy_hp = enemy.base_hp

    hero_speed = hero.get_speed()
    turn = "hero" if hero_speed >= enemy.speed else "enemy"

    while hero_hp > 0 and enemy_hp > 0:
        if turn == "hero":
            dmg = calculate_damage(hero.get_attack(), ability.power, enemy.defense)
            enemy_hp -= dmg
            log.append(f"{hero.hero.name} (Lvl {hero.get_level()}) usa {ability.name} y hace {dmg} de daño a {enemy.name}.")
            turn = "enemy"
        else:
            dmg = calculate_damage(enemy.attack, ability.power, hero.get_defense())
            hero_hp -= dmg
            log.append(f"{enemy.name} ataca y hace {dmg} de daño a {hero.hero.name}.")
            turn = "hero"

    winner = "hero" if hero_hp > 0 else "enemy"
    log.append(f"Gana el {winner.upper()}")
    return SimpleCombatResult(winner, log)
