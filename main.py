import sys

from rpg import items
from rpg.camp import Merchant
from rpg.combat import Outcome
from rpg.hero import Hero, HeroClass
from rpg.items import Item, ItemCatalog, default_catalog
from rpg.view import ConsoleView
from rpg.world import Crypt, DragonLair, Forest, LocationRegistry

VIEW = ConsoleView()


def read_choice(count: int) -> int:
    """Reads a number from 1 to count, returns the index or -1 for anything else."""
    try:
        choice = int(input().strip())
    except ValueError:
        return -1
    return choice - 1 if 1 <= choice <= count else -1


def create_hero(catalog: ItemCatalog) -> Hero:
    print("Создайте своего героя!")
    while True:
        print("Выберите класс:")
        hero_classes = list(HeroClass)
        for i, hero_class in enumerate(hero_classes, start=1):
            kit = hero_class.get_starter_kit(catalog)
            print(
                f"{i} - {hero_class.display_name} (здоровье {hero_class.base_health}): "
                f"{VIEW.describe(kit.create_weapon())}, {VIEW.describe(kit.create_armor())}"
            )
        index = read_choice(len(hero_classes))
        if index < 0:
            continue
        hero_class = hero_classes[index]

        print("Введите имя:")
        name = input().strip()

        try:
            return (
                Hero.Builder()
                .set_name(name)
                .set_hero_class(hero_class)
                .set_starter_kit(hero_class.get_starter_kit(catalog))
                .build()
            )
        except ValueError as e:
            print(f"Не получилось создать героя: {e}")


def go_on_expedition(hero: Hero, locations: LocationRegistry) -> None:
    all_locations = locations.get_all()
    print("Куда отправимся?")
    for i, location in enumerate(all_locations, start=1):
        print(f"{i} - {location.display_name} (рекомендуемый уровень {location.recommended_level})")
    index = read_choice(len(all_locations))
    if index < 0:
        return

    location = all_locations[index]
    report = location.explore(hero)
    print()
    VIEW.print_report(report, location.display_name)

    if report.battle.outcome == Outcome.VICTORY and location.code == DragonLair.CODE:
        print(f"\nДракон повержен! Барды еще долго будут петь о подвиге героя по имени {hero.name}.")


def manage_equipment(hero: Hero) -> None:
    inventory = list(hero.inventory)
    if not inventory:
        print("Инвентарь пуст")
        return

    print("Что экипировать? (0 - назад)")
    for i, item in enumerate(inventory, start=1):
        print(f"{i} - {VIEW.describe(item)}")
    index = read_choice(len(inventory))
    if index < 0:
        return

    item = inventory[index]
    hero.equip(item)
    print("Экипировано: " + VIEW.describe(item))


def visit_merchant(hero: Hero, merchant: Merchant) -> None:
    print(f'Торговец: "Чего желаешь?" (золото: {hero.gold})')
    print("1 - купить, 2 - продать, 0 - назад")
    choice = input().strip()
    if choice == "1":
        buy(hero, merchant)
    elif choice == "2":
        sell(hero, merchant)


def buy(hero: Hero, merchant: Merchant) -> None:
    showcase = merchant.get_showcase()
    for i, item in enumerate(showcase, start=1):
        print(f"{i} - {VIEW.describe(item)}: {item.price} золота")
    index = read_choice(len(showcase))
    if index < 0:
        return

    try:
        item = merchant.buy(hero, showcase[index].code)
        print("Куплено: " + VIEW.describe(item))
    except RuntimeError as e:
        print(e)


def sell(hero: Hero, merchant: Merchant) -> None:
    inventory = list(hero.inventory)
    if not inventory:
        print("Продавать нечего (экипированные предметы продать нельзя)")
        return

    for i, item in enumerate(inventory, start=1):
        print(f"{i} - {VIEW.describe(item)}: {merchant.get_sell_price(item)} золота")
    index = read_choice(len(inventory))
    if index < 0:
        return

    item = inventory[index]
    price = merchant.sell(hero, item)
    print(f"Продано: {item.name} за {price} золота")


def main() -> None:
    catalog = default_catalog()
    locations = LocationRegistry([Forest(catalog), Crypt(catalog), DragonLair(catalog)])
    merchant = Merchant(
        catalog,
        [items.IRON_SWORD, items.ELVEN_BOW, items.EMBER_STAFF, items.CHAINMAIL, items.PLATE_ARMOR],
    )

    hero = create_hero(catalog)
    print(f"{hero.name} разбивает лагерь на опушке мистического леса.")

    while True:
        print()
        VIEW.print_hero(hero)
        print("1 - отправиться в экспедицию, 2 - снаряжение, 3 - торговец, 0 - выйти из игры")
        choice = input().strip()
        if choice == "1":
            go_on_expedition(hero, locations)
        elif choice == "2":
            manage_equipment(hero)
        elif choice == "3":
            visit_merchant(hero, merchant)
        elif choice == "0":
            return
        else:
            print("Такого варианта нет")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print()
