# Лаба 3 — Порождающие шаблоны проектирования (Python)

Текстовая RPG: герой ходит в экспедиции и сражается с врагами.

Запуск (Python 3.10+):

    python main.py   # сама игра
    python demo.py   # демонстрация всех 5 паттернов

| Паттерн | Где в коде |
|---|---|
| Одиночка (Singleton) | `rpg/core.py` — `Dice` |
| Строитель (Builder) | `rpg/hero.py` — `Hero.Builder` |
| Фабричный метод (Factory Method) | `rpg/world.py` — `Location.create_enemy()` (`Forest`, `Crypt`, `DragonLair`) |
| Абстрактная фабрика (Abstract Factory) | `rpg/kit.py` — `StarterKitFactory` (`WarriorKitFactory`, `RangerKitFactory`, `MageKitFactory`) |
| Прототип (Prototype) | `rpg/items.py` — `Item.copy()`, `ItemCatalog.create()` |
