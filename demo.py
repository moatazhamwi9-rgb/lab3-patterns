import sys

from rpg import items
from rpg.core import Dice
from rpg.hero import Hero, HeroClass
from rpg.items import default_catalog
from rpg.view import ConsoleView
from rpg.world import Crypt, Forest


def main() -> None:
    catalog = default_catalog()
    view = ConsoleView()

    print("===== Одиночка =====")
    first = Dice.get_instance()
    second = Dice.get_instance()
    third = Dice()  # even a direct constructor call gives the same object
    print("Dice.get_instance() возвращает один и тот же объект:", first is second)
    print("Dice() тоже возвращает тот же объект:", first is third)

    print()
    print("===== Прототип =====")
    plain_sword = catalog.create(items.IRON_SWORD)
    fiery_sword = catalog.create(items.IRON_SWORD)
    fiery_sword.enchant(items.FIERY)
    print("Первая копия:        " + view.describe(plain_sword))
    print("Вторая копия:        " + view.describe(fiery_sword))
    print("Новая копия шаблона: " + view.describe(catalog.create(items.IRON_SWORD)))
    print("Копии - разные объекты:", plain_sword is not fiery_sword)

    print()
    print("===== Абстрактная фабрика =====")
    for hero_class in HeroClass:
        kit = hero_class.get_starter_kit(catalog)
        print(
            f"{hero_class.display_name}: {view.describe(kit.create_weapon())}, "
            f"{view.describe(kit.create_armor())}"
        )

    print()
    print("===== Строитель =====")
    hero = (
        Hero.Builder()
        .set_name("Артур")
        .set_hero_class(HeroClass.WARRIOR)
        .set_starter_kit(HeroClass.WARRIOR.get_starter_kit(catalog))
        .set_level(3)
        .build()
    )
    view.print_hero(hero)
    try:
        Hero.Builder().set_hero_class(HeroClass.MAGE).set_starter_kit(
            HeroClass.MAGE.get_starter_kit(catalog)
        ).build()
    except ValueError as e:
        print("Герой без имени не создается:", e)
    try:
        Hero.Builder().set_name("Мерлин").build()
    except ValueError as e:
        print("Герой без класса не создается:", e)

    print()
    print("===== Фабричный метод =====")
    forest = Forest(catalog)
    crypt = Crypt(catalog)
    view.print_report(forest.explore(hero, 7), forest.display_name)
    print()
    view.print_report(crypt.explore(hero, 7), crypt.display_name)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
