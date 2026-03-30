# PawPal+ Class Diagram (Final Implementation)

```mermaid
classDiagram
    class Owner {
        -str name
        -int available_minutes
        -list~Pet~ pets
        +get_name() str
        +get_available_minutes() int
        +add_pet(pet: Pet) None
        +get_pets() list~Pet~
        +get_all_tasks() list~Task~
        +filter_by_pet(pet_name: str) list~Task~
    }

    class Pet {
        -str name
        -str species
        -int age
        -list~Task~ tasks
        +get_name() str
        +get_species() str
        +get_age() int
        +add_task(task: Task) None
        +get_tasks() list~Task~
        +complete_task(task: Task) Task|None
    }

    class Task {
        -str title
        -int duration_minutes
        -str priority
        -str category
        -str frequency
        -str preferred_time
        -str scheduled_day
        -date|None due_date
        -bool completed
        +get_title() str
        +get_duration() int
        +get_priority() str
        +get_category() str
        +get_due_date() date|None
        +mark_complete() None
        +is_complete() bool
        +reset_if_recurring() None
    }

    class Scheduler {
        -Owner owner
        -Pet pet
        -list~Task~ available_tasks
        -list~Task~ scheduled_tasks
        -list~dict~ schedule_timeline
        +generate_schedule(day_of_week: str, category: str) list~Task~
        +filter_by_time(minutes: int, day_of_week: str, category: str) list~Task~
        +filter_by_status(completed: bool) list~Task~
        +sort_by_priority(tasks: list~Task~) list~Task~
        +sort_by_duration(tasks: list~Task~, descending: bool) list~Task~
        +assign_start_times(tasks: list~Task~) list~dict~
        +detect_conflicts() list~str~
        +detect_same_pet_overlaps() list~str~
        +detect_owner_level_overlaps() list~str~
        +explain_schedule() str
        -_ranges_overlap(s1: int, e1: int, s2: int, e2: int) bool
    }

    Owner "1" --> "1..*" Pet : has
    Pet "1" --> "0..*" Task : manages
    Pet "1" --> "0..*" Task : creates_next_occurrence_for_recurring
    Scheduler --> Owner : queries
    Scheduler --> Pet : operates_on
    Scheduler --> Task : filters_sorts_schedules
```

## Key Implementation Updates from Initial Design

### Task Enhancements

- **New fields**: `frequency` (daily/weekly/as needed), `preferred_time`, `scheduled_day`, `due_date`, `completed`
- **Recurring behavior**: Tasks can auto-spawn next occurrences via `complete_task()` with advanced due dates (timedelta)
- **New methods**: `mark_complete()`, `is_complete()`, `reset_if_recurring()`, `get_due_date()`

### Pet Enhancements

- **Recurring task support**: `complete_task()` marks a task done and creates a fresh pending copy (for daily/weekly tasks)
- **Explicit task list**: `tasks` field now explicit in diagram (was implicit)

### Owner Enhancements

- **Multi-pet queries**: `filter_by_pet()` retrieves tasks for a specific pet (case-insensitive)
- **All-tasks view**: `get_all_tasks()` flattens tasks across all pets
- **Explicit pet list**: `pets` field now explicit in diagram

### Scheduler Enhancements

- **Flexible filtering**:
  - `filter_by_status()` — pending vs. completed tasks
  - `filter_by_time()` now supports day_of_week and category filtering
- **Flexible sorting**:
  - `sort_by_duration()` — order by time (shortest/longest first)
  - `sort_by_priority()` — still available (high→medium→low with SJF tiebreaker)
- **Conflict detection**:
  - `detect_same_pet_overlaps()` — tasks in same pet overlap in time
  - `detect_owner_level_overlaps()` — owner can't be in two places (multi-pet)
  - `_ranges_overlap()` — static helper for interval arithmetic
- **Data structure expansion**:
  - `scheduled_tasks` — tasks that fit in the schedule
  - `schedule_timeline` — list of dicts with start/end minutes and tasks

### Relationship Changes

- **Pet → Task**: Now includes "creates_next_occurrence_for_recurring" to show auto-creation behavior
- **Scheduler → Owner**: Changed to "queries" (can look up multiple pets)
- **Scheduler → Task**: "filters_sorts_schedules" to show comprehensive task manipulation

```

```
