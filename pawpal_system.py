"""PawPal+ logic layer — backend classes for pet care scheduling."""

from dataclasses import dataclass, field


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "high", "medium", or "low"
    category: str

    def get_title(self) -> str:
        pass

    def get_duration(self) -> int:
        pass

    def get_priority(self) -> str:
        pass

    def get_category(self) -> str:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def get_name(self) -> str:
        pass

    def get_species(self) -> str:
        pass

    def get_age(self) -> int:
        pass

    def add_task(self, task: Task) -> None:
        pass

    def get_tasks(self) -> list[Task]:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: list[Pet] = field(default_factory=list)

    def get_name(self) -> str:
        pass

    def get_available_minutes(self) -> int:
        pass

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_pets(self) -> list[Pet]:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet) -> None:
        self.owner = owner
        self.pet = pet
        self.available_tasks: list[Task] = pet.get_tasks()
        self.scheduled_tasks: list[Task] = []

    def generate_schedule(self) -> list[Task]:
        pass

    def filter_by_time(self, minutes: int) -> list[Task]:
        pass

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        pass

    def explain_schedule(self) -> str:
        pass
