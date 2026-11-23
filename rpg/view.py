from .combat import BattleEvent, BattleReport, EventType, Outcome, Side
from .hero import Hero
from .items import Item
from .world import ExpeditionReport, Rewards


class ConsoleView:
    """All console output lives here, so game logic does not depend on the console."""

    def describe(self, item: Item) -> str:
        text = item.name
        if item.enchantments:
            names = ", ".join(e.name for e in item.enchantments)
            text += f" [{names}]"
        return f"{text} ({item.description()})"

    def print_hero(self, hero: Hero) -> None:
        print(
            f"{hero.name}, {hero.hero_class.display_name} {hero.level} ур. | "
            f"здоровье {hero.max_health} | опыт {hero.experience}/{hero.experience_to_next_level} | "
            f"золото {hero.gold}"
        )
        print("  Оружие: " + self.describe(hero.weapon))
        print("  Броня:  " + self.describe(hero.armor))

    def print_report(self, report: ExpeditionReport, location_name: str) -> None:
        battle = report.battle
        print(f"=== {location_name} (сид {report.seed}) ===")
        print(
            f"{battle.hero.name} встречает врага: {battle.enemy.name} "
            f"({battle.enemy.max_health} здоровья)"
        )
        for event in battle.events:
            self._print_event(event, battle)
        self._print_rewards(battle, report.rewards)

    def _print_event(self, event: BattleEvent, battle: BattleReport) -> None:
        source = self._participant(event.source, battle)
        target = self._participant(event.target, battle)

        if event.type == EventType.HIT:
            print(
                f"[раунд {event.round}] {source.name} -> {target.name}: {event.amount} урона, "
                f"осталось {event.target_health_after}/{target.max_health}"
            )
        elif event.type == EventType.CRITICAL_HIT:
            print(
                f"[раунд {event.round}] {source.name} -> {target.name}: КРИТ! {event.amount} урона, "
                f"осталось {event.target_health_after}/{target.max_health}"
            )
        elif event.type == EventType.DEATH:
            print(f"{target.name} повержен!")

    def _print_rewards(self, battle: BattleReport, rewards: Rewards) -> None:
        if battle.outcome == Outcome.DEFEAT:
            print(f"Поражение... {battle.hero.name} едва уносит ноги и теряет {-rewards.gold} золота")
            return

        print(f"Победа! +{rewards.experience} опыта, +{rewards.gold} золота")
        if rewards.loot is not None:
            print("Добыча: " + self.describe(rewards.loot))
        if rewards.levels_gained > 0:
            print("Новый уровень!")

    @staticmethod
    def _participant(side: Side, battle: BattleReport):
        return battle.hero if side == Side.HERO else battle.enemy
