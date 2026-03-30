"""PawPal+ logic layer — backend classes for pet care scheduling."""

from dataclasses import dataclass, field


PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str        # "high", "medium", or "low"
    category: str
    frequency: str = "daily"   # e.g. "daily", "weekly", "as needed"
    completed: bool = False

    def get_title(self) -> str:
        """Return the task title."""
        return self.title

    def get_duration(self) -> int:
        """Return the task duration in minutes."""
        return self.duration_minutes

    def get_priority(self) -> str:
        """Return the task priority level."""
        return self.priority

    def get_category(self) -> str:
        """Return the task category."""
        return self.category

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_complete(self) -> bool:
        """Return True if the task has been completed."""
        return self.completed


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def get_name(self) -> str:
        """Return the pet's name."""
        return self.name

    def get_species(self) -> str:
        """Return the pet's species."""
        return self.species

    def get_age(self) -> int:
        """Return the pet's age in years."""
        return self.age

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return a copy of this pet's task list."""
        return list(self.tasks)


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: list[Pet] = field(default_factory=list)

    def get_name(self) -> str:
        """Return the owner's name."""
        return self.name

    def get_available_minutes(self) -> int:
        """Return the number of minutes the owner has available today."""
        return self.available_minutes

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def get_pets(self) -> list[Pet]:
        """Return a copy of this owner's pet list."""
        return list(self.pets)

    def get_all_tasks(self) -> list[Task]:
        """Return a flat list of every task across all owned pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet) -> None:
        self.owner = owner
        self.pet = pet
        self.available_tasks: list[Task] = pet.get_tasks()
        self.scheduled_tasks: list[Task] = []

    def generate_schedule(self) -> list[Task]:
        """Filter tasks that fit within available time, then sort by priority."""
        time_limit = self.owner.get_available_minutes()
        fits = self.filter_by_time(time_limit)
        self.scheduled_tasks = self.sort_by_priority(fits)
        return self.scheduled_tasks

    def filter_by_time(self, minutes: int) -> list[Task]:
        """Return tasks whose total cumulative duration fits within `minutes`."""
        result = []
        time_used = 0
        # Sort by priority first so we keep the most important tasks when time is tight
        candidates = self.sort_by_priority(self.available_tasks)
        for task in candidates:
            if time_used + task.get_duration() <= minutes:
                result.append(task)
                time_used += task.get_duration()
        return result

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted high → medium → low priority."""
        return sorted(tasks, key=lambda t: PRIORITY_RANK.get(t.get_priority(), 99))

    def explain_schedule(self) -> str:
        """Return a human-readable summary of the generated schedule."""
        if not self.scheduled_tasks:
            return "No schedule generated yet. Call generate_schedule() first."

        total_minutes = sum(t.get_duration() for t in self.scheduled_tasks)
        lines = [
            f"Schedule for {self.pet.get_name()} "
            f"({self.owner.get_name()}, {self.owner.get_available_minutes()} min available)",
            f"Total time: {total_minutes} min across {len(self.scheduled_tasks)} task(s)",
            "",
        ]
        for i, task in enumerate(self.scheduled_tasks, start=1):
            lines.append(
                f"{i}. [{task.get_priority().upper()}] {task.get_title()} "
                f"— {task.get_duration()} min ({task.get_category()}, {task.frequency})"
            )

        skipped = [t for t in self.available_tasks if t not in self.scheduled_tasks]
        if skipped:
            lines.append("")
            lines.append("Skipped (not enough time):")
            for task in skipped:
                lines.append(f"  - {task.get_title()} ({task.get_duration()} min)")

        return "\n".join(lines)
