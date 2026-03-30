"""Temporary testing ground for PawPal+ logic."""

from pawpal_system import Owner, Pet, Task, Scheduler


# --- Build tasks ---
walk = Task(title="Morning Walk", duration_minutes=30, priority="high", category="exercise", frequency="daily")
feed = Task(title="Breakfast Feeding", duration_minutes=10, priority="high", category="nutrition", frequency="daily")
grooming = Task(title="Brush Coat", duration_minutes=15, priority="medium", category="grooming", frequency="weekly")
playtime = Task(title="Fetch / Playtime", duration_minutes=20, priority="medium", category="enrichment", frequency="daily")
vet_meds = Task(title="Administer Medication", duration_minutes=5, priority="high", category="health", frequency="daily")
litter_box = Task(title="Clean Litter Box", duration_minutes=10, priority="high", category="hygiene", frequency="daily")
cat_play = Task(title="Wand Toy Play", duration_minutes=15, priority="medium", category="enrichment", frequency="daily")

# --- Build pets ---
dog = Pet(name="Biscuit", species="Dog", age=3)
dog.add_task(walk)
dog.add_task(feed)
dog.add_task(grooming)
dog.add_task(playtime)

cat = Pet(name="Mochi", species="Cat", age=5)
cat.add_task(vet_meds)
cat.add_task(litter_box)
cat.add_task(cat_play)

# --- Build owner ---
owner = Owner(name="Michelle", available_minutes=60)
owner.add_pet(dog)
owner.add_pet(cat)

# --- Run scheduler for each pet and print ---
print("=" * 50)
print("         TODAY'S PAWPAL+ SCHEDULE")
print("=" * 50)

for pet in owner.get_pets():
    scheduler = Scheduler(owner=owner, pet=pet)
    scheduler.generate_schedule()
    print()
    print(scheduler.explain_schedule())
    print("-" * 50)
