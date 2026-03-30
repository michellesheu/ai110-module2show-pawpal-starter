"""PawPal+ demo — exercises sorting, filtering, recurring tasks, and conflict detection."""

from datetime import date

from pawpal_system import Owner, Pet, Task, Scheduler


# ── Build pets and add tasks OUT OF ORDER ────────────────────────────
# Tasks are deliberately added in a scrambled order (not sorted by
# duration or priority) so that the sorting/filtering output below
# proves the methods actually reorder them.

today = date.today()

dog = Pet(name="Biscuit", species="Dog", age=3)
dog.add_task(Task(title="Fetch / Playtime",      duration_minutes=20, priority="medium", category="enrichment", frequency="daily",  due_date=today))
dog.add_task(Task(title="Morning Walk",           duration_minutes=30, priority="high",   category="exercise",   frequency="daily",  due_date=today))
dog.add_task(Task(title="Brush Coat",             duration_minutes=15, priority="medium", category="grooming",   frequency="weekly", scheduled_day="monday", due_date=today))
dog.add_task(Task(title="Breakfast Feeding",      duration_minutes=10, priority="high",   category="nutrition",  frequency="daily",  due_date=today))
dog.add_task(Task(title="Evening Run",            duration_minutes=25, priority="low",    category="exercise",   frequency="daily",  due_date=today))

cat = Pet(name="Mochi", species="Cat", age=5)
cat.add_task(Task(title="Wand Toy Play",          duration_minutes=15, priority="medium", category="enrichment", frequency="daily",  due_date=today))
cat.add_task(Task(title="Clean Litter Box",       duration_minutes=10, priority="high",   category="hygiene",    frequency="daily",  due_date=today))
cat.add_task(Task(title="Administer Medication",  duration_minutes=5,  priority="high",   category="health",     frequency="daily",  due_date=today))
cat.add_task(Task(title="Wet Food Dinner",        duration_minutes=10, priority="high",   category="nutrition",  frequency="daily",  due_date=today))

owner = Owner(name="Michelle", available_minutes=60)
owner.add_pet(dog)
owner.add_pet(cat)

print("Tasks were added in this order for Biscuit:")
for t in dog.get_tasks():
    print(f"  {t.get_duration():>3} min  [{t.get_priority():<6}]  {t.get_title()}")


# =====================================================================
# 1.  SORTING TASKS BY TIME
# =====================================================================
print()
print("=" * 55)
print("  1. SORT BY DURATION")
print("=" * 55)

scheduler_dog = Scheduler(owner=owner, pet=dog)

print()
print("  Shortest → longest:")
for t in scheduler_dog.sort_by_duration(dog.get_tasks()):
    print(f"    {t.get_duration():>3} min  | {t.get_title()}")

print()
print("  Longest → shortest:")
for t in scheduler_dog.sort_by_duration(dog.get_tasks(), descending=True):
    print(f"    {t.get_duration():>3} min  | {t.get_title()}")

print()
print("  Sort by priority (high→med→low, then shortest-first):")
for t in scheduler_dog.sort_by_priority(dog.get_tasks()):
    print(f"    {t.get_duration():>3} min  [{t.get_priority():<6}]  {t.get_title()}")


# =====================================================================
# 2.  FILTERING BY PET / STATUS
# =====================================================================
print()
print("=" * 55)
print("  2. FILTER BY PET & STATUS")
print("=" * 55)

# Filter by pet name
print()
print("  All of Mochi's tasks (via owner.filter_by_pet):")
for t in owner.filter_by_pet("Mochi"):
    print(f"    - {t.get_title()} [{t.get_priority()}]")

print()
print("  All of Biscuit's tasks (via owner.filter_by_pet):")
for t in owner.filter_by_pet("Biscuit"):
    print(f"    - {t.get_title()} [{t.get_priority()}]")

# Mark two tasks complete using complete_task(), then filter by status
morning_walk = dog.tasks[1]       # Morning Walk (added 2nd)
breakfast    = dog.tasks[3]       # Breakfast Feeding (added 4th)
dog.complete_task(morning_walk)   # daily → auto-creates next occurrence
dog.complete_task(breakfast)      # daily → auto-creates next occurrence

# Rebuild scheduler so it sees the updated task list
scheduler_dog = Scheduler(owner=owner, pet=dog)

print()
print("  After completing 'Morning Walk' and 'Breakfast Feeding':")

print("  Incomplete:")
for t in scheduler_dog.filter_by_status(completed=False):
    print(f"    [ ] {t.get_title()}")

print("  Completed:")
for t in scheduler_dog.filter_by_status(completed=True):
    print(f"    [x] {t.get_title()}")


# =====================================================================
# 3.  RECURRING TASK AUTO-CREATION
# =====================================================================
print()
print("=" * 55)
print("  3. RECURRING TASK — AUTO NEXT OCCURRENCE")
print("=" * 55)

print()
print(f"  Biscuit now has {len(dog.get_tasks())} tasks (was 5 before completing 2 daily tasks):")
for t in dog.get_tasks():
    status = "done" if t.is_complete() else "pending"
    due = t.get_due_date() or "no date"
    print(f"    {status:>7}  | {t.get_title()} ({t.frequency})  due: {due}")

print()
print("  The 2 completed daily tasks each spawned a fresh next occurrence")
print("  with due_date = today + 1 day (via timedelta).")
print("  'as needed' or one-off tasks would NOT spawn a new instance.")

# Demo: completing an "as needed" task does NOT create a next occurrence
one_off = Task(title="Vet Checkup", duration_minutes=60, priority="high",
               category="health", frequency="as needed")
dog.add_task(one_off)
result = dog.complete_task(one_off)
print()
print(f"  Completed 'Vet Checkup' (as needed) → next occurrence: {result}")
print(f"  Task count still: {len(dog.get_tasks())} (no new instance created)")


# =====================================================================
# 4.  CONFLICT DETECTION + SCHEDULE GENERATION
# =====================================================================
print()
print("=" * 55)
print("  4. SCHEDULE WITH CONFLICT DETECTION")
print("=" * 55)

for pet in owner.get_pets():
    scheduler = Scheduler(owner=owner, pet=pet)
    scheduler.generate_schedule()

    print()
    print(scheduler.explain_schedule())

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        print()
        print("  Conflicts detected:")
        for w in conflicts:
            print(f"    !! {w}")

    print("-" * 55)

# =====================================================================
# 5.  SAME-PET TIME OVERLAPS (manual schedule with conflicts)
# =====================================================================
print()
print("=" * 55)
print("  5. SAME-PET OVERLAP DETECTION")
print("=" * 55)

print()
print("  Creating a manual schedule with overlapping tasks for Biscuit:")

# Create a scenario with overlapping task times
overlap_pet = Pet(name="Biscuit", species="Dog", age=3)
task_a = Task(title="Morning Walk", duration_minutes=30, priority="high",
              category="exercise", frequency="daily", due_date=today)
task_b = Task(title="Breakfast Feeding", duration_minutes=20, priority="high",
              category="nutrition", frequency="daily", due_date=today)
task_c = Task(title="Playtime", duration_minutes=25, priority="medium",
              category="enrichment", frequency="daily", due_date=today)
overlap_pet.add_task(task_a)
overlap_pet.add_task(task_b)
overlap_pet.add_task(task_c)

# Create a scheduler and manually set overlapping times
overlap_sched = Scheduler(owner=owner, pet=overlap_pet)
# Manually create overlapping timeline:
# Task A: 0-30
# Task B: 10-30 (overlaps with A)
# Task C: 25-50 (overlaps with A and B)
overlap_sched.schedule_timeline = [
    {"task": task_a, "start_minute": 0, "end_minute": 30},
    {"task": task_b, "start_minute": 10, "end_minute": 30},
    {"task": task_c, "start_minute": 25, "end_minute": 50},
]
overlap_sched.scheduled_tasks = [task_a, task_b, task_c]

print()
print("  Manually scheduled timeline:")
for entry in overlap_sched.schedule_timeline:
    print(f"    {entry['task'].get_title():20} | min {entry['start_minute']:2}-{entry['end_minute']:2}")

print()
print("  Calling detect_same_pet_overlaps():")
overlaps_same_pet = overlap_sched.detect_same_pet_overlaps()
if overlaps_same_pet:
    for w in overlaps_same_pet:
        print(f"    !! {w}")
else:
    print("    No overlaps detected.")

# =====================================================================
# 6.  OWNER-LEVEL TIME OVERLAPS (multiple pets)
# =====================================================================
print()
print("=" * 55)
print("  6. OWNER-LEVEL OVERLAP DETECTION")
print("=" * 55)

sched_dog = Scheduler(owner=owner, pet=dog)
overlaps = sched_dog.detect_owner_level_overlaps()

if overlaps:
    print()
    print("  Overlaps detected across pets:")
    for w in overlaps:
        print(f"    !! {w}")
else:
    print()
    print("  No overlaps detected between pets' schedules.")

# ── Day-of-week filtering (grooming only appears on Monday) ──────────
print()
print("=" * 55)
print("  BONUS: Day-of-week filtering for Biscuit")
print("=" * 55)

for day in ["monday", "wednesday"]:
    sched = Scheduler(owner=owner, pet=dog)
    sched.generate_schedule(day_of_week=day)
    task_names = [t.get_title() for t in sched.scheduled_tasks]
    print(f"  {day.capitalize():>12}: {', '.join(task_names)}")
