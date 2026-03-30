"""PawPal+ logic layer — backend classes for pet care scheduling."""

from dataclasses import dataclass, field, replace
from datetime import date, timedelta


PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str        # "high", "medium", or "low"
    category: str
    frequency: str = "daily"      # "daily", "weekly", "as needed"
    preferred_time: str = ""      # "morning", "afternoon", "evening", or ""
    scheduled_day: str = ""       # for weekly tasks: "monday", "tuesday", etc.
    due_date: date | None = None   # when this occurrence is due
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

    def get_due_date(self) -> date | None:
        """Return the task's due date, or None if not set."""
        return self.due_date

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_complete(self) -> bool:
        """Return True if the task has been completed."""
        return self.completed

    def reset_if_recurring(self) -> None:
        """Reset completion status for recurring tasks (daily or weekly)."""
        if self.frequency in ("daily", "weekly"):
            self.completed = False


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

    def complete_task(self, task: Task) -> Task | None:
        """Mark a task complete. If the task is daily or weekly, append a
        fresh next-occurrence copy (with an updated due_date) to this pet's
        task list and return it.
        Returns None for non-recurring ('as needed') tasks."""
        task.mark_complete()
        if task.frequency in ("daily", "weekly"):
            base = task.due_date if task.due_date else date.today()
            if task.frequency == "daily":
                next_due = base + timedelta(days=1)
            else:  # weekly
                next_due = base + timedelta(weeks=1)
            next_occurrence = replace(task, completed=False, due_date=next_due)
            self.tasks.append(next_occurrence)
            return next_occurrence
        return None


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

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        """Return tasks for the pet matching pet_name (case-insensitive)."""
        for pet in self.pets:
            if pet.get_name().lower() == pet_name.lower():
                return pet.get_tasks()
        return []


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet) -> None:
        self.owner = owner
        self.pet = pet
        self.available_tasks: list[Task] = pet.get_tasks()
        self.scheduled_tasks: list[Task] = []
        self.schedule_timeline: list[dict] = []  # [{task, start_minute, end_minute}]

    def generate_schedule(self, day_of_week: str = "", category: str = "") -> list[Task]:
        """Build a schedule: filter by time/day/category, then assign start times."""
        time_limit = self.owner.get_available_minutes()
        self.scheduled_tasks = self.filter_by_time(time_limit, day_of_week=day_of_week, category=category)
        self.schedule_timeline = self.assign_start_times(self.scheduled_tasks)
        return self.scheduled_tasks

    def filter_by_time(self, minutes: int, day_of_week: str = "", category: str = "") -> list[Task]:
        """Return tasks that are incomplete, match the day/category filter, and fit within `minutes`."""
        # Drop already-completed tasks
        candidates = [t for t in self.available_tasks if not t.is_complete()]

        # For weekly tasks, skip those not scheduled for today
        if day_of_week:
            candidates = [
                t for t in candidates
                if not (t.frequency == "weekly" and t.scheduled_day
                        and t.scheduled_day.lower() != day_of_week.lower())
            ]

        # Optional category filter
        if category:
            candidates = [t for t in candidates if t.get_category().lower() == category.lower()]

        # Sort: priority first, then shortest-first within same priority (SJF tiebreaker)
        candidates = self.sort_by_priority(candidates)

        result = []
        time_used = 0
        for task in candidates:
            if time_used + task.get_duration() <= minutes:
                result.append(task)
                time_used += task.get_duration()
        return result

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted high→medium→low, shortest-first within the same priority."""
        return sorted(tasks, key=lambda t: (PRIORITY_RANK.get(t.get_priority(), 99), t.get_duration()))

    def sort_by_duration(self, tasks: list[Task], descending: bool = False) -> list[Task]:
        """Return tasks sorted by duration (shortest-first by default)."""
        return sorted(tasks, key=lambda t: t.get_duration(), reverse=descending)

    def filter_by_status(self, completed: bool = False) -> list[Task]:
        """Return tasks that match the given completion status."""
        return [t for t in self.available_tasks if t.is_complete() == completed]

    def assign_start_times(self, tasks: list[Task]) -> list[dict]:
        """Assign sequential start/end times (in minutes from 0) to scheduled tasks."""
        timeline = []
        current = 0
        for task in tasks:
            timeline.append({
                "task": task,
                "start_minute": current,
                "end_minute": current + task.get_duration(),
            })
            current += task.get_duration()
        return timeline

    @staticmethod
    def _ranges_overlap(start1: int, end1: int, start2: int, end2: int) -> bool:
        """Check if two time ranges [start1, end1) and [start2, end2) overlap."""
        return start1 < end2 and start2 < end1

    def detect_same_pet_overlaps(self) -> list[str]:
        """Detect if any tasks in this pet's schedule overlap in time."""
        warnings = []
        timeline = self.schedule_timeline
        for i in range(len(timeline)):
            for j in range(i + 1, len(timeline)):
                entry_i = timeline[i]
                entry_j = timeline[j]
                if self._ranges_overlap(entry_i["start_minute"], entry_i["end_minute"],
                                        entry_j["start_minute"], entry_j["end_minute"]):
                    warnings.append(
                        f"Time overlap for {self.pet.get_name()}: "
                        f"'{entry_i['task'].get_title()}' (min {entry_i['start_minute']}-{entry_i['end_minute']}) "
                        f"overlaps with '{entry_j['task'].get_title()}' "
                        f"(min {entry_j['start_minute']}-{entry_j['end_minute']})."
                    )
        return warnings

    def detect_owner_level_overlaps(self) -> list[str]:
        """Detect overlaps across all pets owned by the owner.
        Requires generating schedules for each pet first."""
        warnings = []
        pets = self.owner.get_pets()

        # Build a schedule for each pet
        schedules = {}
        for pet in pets:
            sched = Scheduler(owner=self.owner, pet=pet)
            sched.generate_schedule()
            schedules[pet.get_name()] = sched.schedule_timeline

        # Check for overlaps across different pets
        pet_names = list(schedules.keys())
        for i in range(len(pet_names)):
            for j in range(i + 1, len(pet_names)):
                pet_i, pet_j = pet_names[i], pet_names[j]
                timeline_i, timeline_j = schedules[pet_i], schedules[pet_j]

                for entry_i in timeline_i:
                    for entry_j in timeline_j:
                        if self._ranges_overlap(entry_i["start_minute"], entry_i["end_minute"],
                                                entry_j["start_minute"], entry_j["end_minute"]):
                            warnings.append(
                                f"Owner time conflict: {pet_i}'s '{entry_i['task'].get_title()}' "
                                f"(min {entry_i['start_minute']}-{entry_i['end_minute']}) "
                                f"overlaps with {pet_j}'s '{entry_j['task'].get_title()}' "
                                f"(min {entry_j['start_minute']}-{entry_j['end_minute']})."
                            )

        return warnings

    def detect_conflicts(self) -> list[str]:
        """Return a list of conflict warnings for the current schedule."""
        warnings = []

        # Back-to-back tasks in the same category (no rest gap)
        for i in range(len(self.schedule_timeline) - 1):
            curr = self.schedule_timeline[i]
            nxt = self.schedule_timeline[i + 1]
            if (curr["task"].get_category() == nxt["task"].get_category()
                    and curr["end_minute"] == nxt["start_minute"]):
                warnings.append(
                    f"Back-to-back '{curr['task'].get_category()}' tasks: "
                    f"'{curr['task'].get_title()}' then '{nxt['task'].get_title()}' — consider a break."
                )

        # Total time overrun guard (should not happen normally, but catches edge cases)
        total = sum(t.get_duration() for t in self.scheduled_tasks)
        if total > self.owner.get_available_minutes():
            warnings.append(
                f"Schedule exceeds available time: {total} min scheduled vs "
                f"{self.owner.get_available_minutes()} min available."
            )

        # Check for overlaps in the same pet's schedule
        warnings.extend(self.detect_same_pet_overlaps())

        return warnings

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

        for entry in self.schedule_timeline:
            task = entry["task"]
            start = entry["start_minute"]
            end = entry["end_minute"]
            lines.append(
                f"  min {start:>3}–{end:<3}  [{task.get_priority().upper()}] {task.get_title()} "
                f"— {task.get_duration()} min ({task.get_category()}, {task.frequency})"
            )

        conflicts = self.detect_conflicts()
        if conflicts:
            lines.append("")
            lines.append("Warnings:")
            for w in conflicts:
                lines.append(f"  ! {w}")

        # Split skipped tasks into two buckets: already done vs didn't fit
        completed_skipped = [t for t in self.available_tasks if t.is_complete()]
        time_skipped = [
            t for t in self.available_tasks
            if not t.is_complete() and t not in self.scheduled_tasks
        ]

        if completed_skipped:
            lines.append("")
            lines.append("Already completed (skipped):")
            for t in completed_skipped:
                lines.append(f"  - {t.get_title()} ({t.get_duration()} min)")

        if time_skipped:
            lines.append("")
            lines.append("Skipped (not enough time):")
            for t in time_skipped:
                lines.append(f"  - {t.get_title()} ({t.get_duration()} min)")

        return "\n".join(lines)
