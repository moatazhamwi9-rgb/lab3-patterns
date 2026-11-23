from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from . import items
from .combat import Battle, BattleReport, Outcome
from .core import Dice, UnknownCodeError
from .enemies import Dragon, Enemy, Goblin, Skeleton
from .hero import Hero
from .items import Item, ItemCatalog


@dataclass(frozen=True)
class Rewards:
    """gold is negative if the hero lost gold; loot is None if there is no loot."""
    experience: int
    gold: int
    loot: Optional[Item]
    levels_gained: int


@dataclass(frozen=True)
class ExpeditionReport:
    seed: int
    location_code: str
    battle: BattleReport
    rewards: Rewards


class Location(ABC):
    """Creator of the Factory Method (Фабричный метод).

    explore() is the common logic (it is also a Template Method);
    create_enemy() is the factory method that subclasses implement.
    """

    LOOT_CHANCE = 0.6
    ENCHANT_CHANCE = 0.3

    def __init__(self, code: str, display_name: str, recommended_level: int, catalog: ItemCatalog):
        self._code = code
        self._display_name = display_name
        self._recommended_level = recommended_level
        self._catalog = catalog

    @abstractmethod
    def create_enemy(self) -> Enemy:
        """Factory method: which enemy lives here is decided by subclasses."""

    @abstractmethod
    def get_loot_table(self) -> list:
        """Codes of the items from the catalog that can be found here."""

    def explore(self, hero: Hero, seed: Optional[int] = None) -> ExpeditionReport:
        dice = Dice()
        if seed is None:
            seed = dice.next_seed()
        dice.reseed(seed)

        hero.restore_health()
        enemy = self.create_enemy()  # the base class does not know which enemy
        battle = Battle(hero, enemy).run()

        if battle.outcome == Outcome.VICTORY:
            rewards = self._reward(hero, enemy, dice)
        else:
            rewards = self._punish(hero)

        return ExpeditionReport(seed, self._code, battle, rewards)

    def _reward(self, hero, enemy, dice) -> Rewards:
        experience = enemy.experience_reward
        gold = enemy.roll_gold_reward()
        loot = self._roll_loot(dice)

        levels_gained = hero.gain_experience(experience)
        hero.add_gold(gold)
        if loot is not None:
            hero.add_item(loot)

        return Rewards(experience, gold, loot, levels_gained)

    def _roll_loot(self, dice) -> Optional[Item]:
        if not dice.chance(self.LOOT_CHANCE):
            return None

        # loot is a COPY of a catalog template, so enchanting it is safe
        loot = self._catalog.create(dice.pick(self.get_loot_table()))
        if dice.chance(self.ENCHANT_CHANCE):
            loot.enchant(dice.pick(list(loot.possible_enchantments())))
        return loot

    def _punish(self, hero) -> Rewards:
        # a defeated hero loses half of the gold
        lost = hero.gold // 2
        hero.spend_gold(lost)
        return Rewards(0, -lost, None, 0)

    @property
    def code(self) -> str:
        return self._code

    @property
    def display_name(self) -> str:
        return self._display_name

    @property
    def recommended_level(self) -> int:
        return self._recommended_level


class Forest(Location):
    CODE = "forest"

    def __init__(self, catalog: ItemCatalog):
        super().__init__(self.CODE, "Мистический лес", 1, catalog)

    def create_enemy(self) -> Enemy:
        return Goblin()

    def get_loot_table(self) -> list:
        return [items.GOBLIN_CLEAVER, items.HUNTING_BOW, items.LEATHER_ARMOR]


class Crypt(Location):
    CODE = "crypt"

    def __init__(self, catalog: ItemCatalog):
        super().__init__(self.CODE, "Заброшенный склеп", 3, catalog)

    def create_enemy(self) -> Enemy:
        return Skeleton()

    def get_loot_table(self) -> list:
        return [items.KNIGHT_BLADE, items.BONE_BOW, items.NECROMANCER_STAFF, items.CRYPT_MAIL]


class DragonLair(Location):
    CODE = "dragon-lair"

    def __init__(self, catalog: ItemCatalog):
        super().__init__(self.CODE, "Логово дракона", 5, catalog)

    def create_enemy(self) -> Enemy:
        return Dragon()

    def get_loot_table(self) -> list:
        return [items.DAWN_BLADE, items.DRAGONSCALE_ARMOR]


class LocationRegistry:
    def __init__(self, locations: list):
        self._locations = {location.code: location for location in locations}

    def get(self, code: str) -> Location:
        location = self._locations.get(code)
        if location is None:
            raise UnknownCodeError("Локация", code)
        return location

    def get_all(self) -> list:
        return list(self._locations.values())
