from abc import ABC, abstractmethod

from . import items
from .items import Armor, ItemCatalog, Weapon


class StarterKitFactory(ABC):
    """Abstract Factory (Абстрактная фабрика): a family of starter equipment."""

    @abstractmethod
    def create_weapon(self) -> Weapon: ...

    @abstractmethod
    def create_armor(self) -> Armor: ...


class WarriorKitFactory(StarterKitFactory):
    def __init__(self, catalog: ItemCatalog):
        self._catalog = catalog

    def create_weapon(self) -> Weapon:
        return self._catalog.create_weapon(items.TRAINING_SWORD)

    def create_armor(self) -> Armor:
        return self._catalog.create_armor(items.CHAINMAIL)


class RangerKitFactory(StarterKitFactory):
    def __init__(self, catalog: ItemCatalog):
        self._catalog = catalog

    def create_weapon(self) -> Weapon:
        return self._catalog.create_weapon(items.HUNTING_BOW)

    def create_armor(self) -> Armor:
        return self._catalog.create_armor(items.LEATHER_ARMOR)


class MageKitFactory(StarterKitFactory):
    def __init__(self, catalog: ItemCatalog):
        self._catalog = catalog

    def create_weapon(self) -> Weapon:
        return self._catalog.create_weapon(items.APPRENTICE_STAFF)

    def create_armor(self) -> Armor:
        return self._catalog.create_armor(items.LINEN_ROBE)
