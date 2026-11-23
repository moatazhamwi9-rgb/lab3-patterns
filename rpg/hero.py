from enum import Enum

from .combat import Combatant, Hit
from .core import UnknownCodeError
from .items import Armor, Item, ItemCatalog, Weapon
from .kit import MageKitFactory, RangerKitFactory, StarterKitFactory, WarriorKitFactory

MAX_NAME_LENGTH = 20
STARTING_GOLD = 50
HEALTH_PER_LEVEL = 15
DAMAGE_PER_LEVEL = 3
EXPERIENCE_PER_LEVEL = 100


class HeroClass(Enum):
    # each class knows its own starter-kit factory
    WARRIOR = ("warrior", "Воин", 120, WarriorKitFactory)
    RANGER = ("ranger", "Следопыт", 100, RangerKitFactory)
    MAGE = ("mage", "Маг", 85, MageKitFactory)

    def __init__(self, code, display_name, base_health, kit_factory_class):
        self.code = code
        self.display_name = display_name
        self.base_health = base_health
        self._kit_factory_class = kit_factory_class

    def get_starter_kit(self, catalog: ItemCatalog) -> StarterKitFactory:
        return self._kit_factory_class(catalog)

    @staticmethod
    def by_code(code: str) -> "HeroClass":
        for hero_class in HeroClass:
            if hero_class.code == code:
                return hero_class
        raise UnknownCodeError("Класс героя", code)


class Hero(Combatant):
    class Builder:
        """Builder (Строитель): step-by-step creation with validation in build()."""

        def __init__(self):
            self._name = None
            self._hero_class = None
            self._weapon = None
            self._armor = None
            # optional fields get defaults right in the builder
            self._level = 1
            self._gold = STARTING_GOLD

        def set_name(self, name):
            self._name = name
            return self

        def set_hero_class(self, hero_class):
            self._hero_class = hero_class
            return self

        def set_weapon(self, weapon):
            self._weapon = weapon
            return self

        def set_armor(self, armor):
            self._armor = armor
            return self

        def set_starter_kit(self, starter_kit: StarterKitFactory):
            self._weapon = starter_kit.create_weapon()
            self._armor = starter_kit.create_armor()
            return self

        def set_level(self, level):
            self._level = level
            return self

        def set_gold(self, gold):
            self._gold = gold
            return self

        def build(self) -> "Hero":
            if self._name is None or not self._name.strip():
                raise ValueError("У героя должно быть имя")
            if len(self._name) > MAX_NAME_LENGTH:
                raise ValueError(f"Имя героя не может быть длиннее {MAX_NAME_LENGTH} символов")
            if self._hero_class is None:
                raise ValueError("Не выбран класс героя")
            if self._weapon is None or self._armor is None:
                raise ValueError("Герою нужны оружие и броня")
            if self._level < 1:
                raise ValueError("Уровень героя не может быть меньше 1")
            if self._gold < 0:
                raise ValueError("Золота не может быть меньше нуля")
            return Hero(self)

    def __init__(self, builder: "Hero.Builder"):
        # the hero takes all values from the builder (create heroes via Hero.Builder)
        self._name = builder._name
        self._hero_class = builder._hero_class
        self._level = builder._level
        self._experience = 0
        self._gold = builder._gold
        self._weapon = builder._weapon
        self._armor = builder._armor
        self._inventory = []
        self._health = self.max_health

    # --- Combatant ---
    def roll_damage(self) -> Hit:
        hit = self._weapon.roll_damage()
        return Hit(hit.damage + (self._level - 1) * DAMAGE_PER_LEVEL, hit.critical)

    def receive_hit(self, damage: int) -> int:
        reduced = round(damage * (1 - self._armor.defense))
        dealt = max(1, reduced)  # armor always lets at least 1 damage through
        self._health = max(0, self._health - dealt)
        return dealt

    def is_alive(self) -> bool:
        return self._health > 0

    # --- between expeditions ---
    def restore_health(self) -> None:
        self._health = self.max_health

    def gain_experience(self, amount: int) -> int:
        """Adds experience, returns the number of gained levels."""
        self._experience += amount
        gained = 0
        while self._experience >= self.experience_to_next_level:
            self._experience -= self.experience_to_next_level
            self._level += 1
            gained += 1
        return gained

    def add_gold(self, amount: int) -> None:
        self._gold += amount

    def spend_gold(self, amount: int) -> None:
        if amount > self._gold:
            raise RuntimeError(f"Не хватает золота: нужно {amount}, есть {self._gold}")
        self._gold -= amount

    def add_item(self, item: Item) -> None:
        self._inventory.append(item)

    def remove_item(self, item: Item) -> None:
        if item not in self._inventory:
            raise ValueError(f"В инвентаре нет предмета {item.name}")
        self._inventory.remove(item)

    def equip(self, item: Item) -> None:
        """Equips an item from the inventory; the old one goes back to the inventory."""
        if isinstance(item, Weapon):
            self.remove_item(item)
            self._inventory.append(self._weapon)
            self._weapon = item
        elif isinstance(item, Armor):
            self.remove_item(item)
            self._inventory.append(self._armor)
            self._armor = item
        else:
            raise ValueError(f"Предмет нельзя экипировать: {item.name}")

    # --- getters ---
    @property
    def code(self) -> str:
        return self._hero_class.code

    @property
    def name(self) -> str:
        return self._name

    @property
    def health(self) -> int:
        return self._health

    @property
    def max_health(self) -> int:
        return self._hero_class.base_health + (self._level - 1) * HEALTH_PER_LEVEL

    @property
    def hero_class(self) -> HeroClass:
        return self._hero_class

    @property
    def level(self) -> int:
        return self._level

    @property
    def experience(self) -> int:
        return self._experience

    @property
    def experience_to_next_level(self) -> int:
        return self._level * EXPERIENCE_PER_LEVEL

    @property
    def gold(self) -> int:
        return self._gold

    @property
    def weapon(self) -> Weapon:
        return self._weapon

    @property
    def armor(self) -> Armor:
        return self._armor

    @property
    def inventory(self) -> tuple:
        return tuple(self._inventory)
