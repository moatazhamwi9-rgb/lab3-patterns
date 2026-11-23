from .core import UnknownCodeError
from .hero import Hero
from .items import Item, ItemCatalog

SELL_PRICE_PERCENT = 50


class Merchant:
    """Sells items from the catalog and buys unneeded ones for half the price."""

    def __init__(self, catalog: ItemCatalog, assortment: list):
        self._catalog = catalog
        self._assortment = list(assortment)

    def get_showcase(self) -> list:
        return [self._catalog.create(code) for code in self._assortment]

    def buy(self, hero: Hero, code: str) -> Item:
        if code not in self._assortment:
            raise UnknownCodeError("Товар", code)

        item = self._catalog.create(code)  # the buyer gets their own copy
        hero.spend_gold(item.price)
        hero.add_item(item)
        return item

    def sell(self, hero: Hero, item: Item) -> int:
        price = self.get_sell_price(item)
        hero.remove_item(item)
        hero.add_gold(price)
        return price

    def get_sell_price(self, item: Item) -> int:
        return item.price * SELL_PRICE_PERCENT // 100
