import random


class UnknownCodeError(Exception):
    """Raised when something is not found by its code (unknown location, item...)."""

    def __init__(self, what: str, code: str):
        super().__init__(f"{what} с кодом '{code}' не существует")


class Dice:
    """Singleton (Одиночка): one source of randomness for the whole game.

    Dice() always returns the same object, so one seed reproduces every roll.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            instance = super().__new__(cls)
            instance._random = random.Random()
            cls._instance = instance
        return cls._instance

    @classmethod
    def get_instance(cls) -> "Dice":
        return cls()

    def reseed(self, seed: int) -> None:
        # after reseed all next rolls repeat exactly
        self._random.seed(seed)

    def next_seed(self) -> int:
        return self._random.randint(0, 999_999)

    def roll(self, low: int, high: int) -> int:
        """Random integer from low to high inclusive."""
        return self._random.randint(low, high)

    def chance(self, probability: float) -> bool:
        return self._random.random() < probability

    def pick(self, options: list):
        return self._random.choice(options)
