# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

This implementation includes several advanced scheduling features:

### Multi-Pet Support
- Owner can manage multiple pets via `Owner.add_pet()`
- Each pet maintains its own task list and schedule
- UI supports pet selector to switch between pets

### Flexible Task Filtering
- **Sort by duration**: `Scheduler.sort_by_duration(tasks, descending=False)` — order tasks shortest-first or longest-first
- **Filter by status**: `Scheduler.filter_by_status(completed=False)` — retrieve pending or completed tasks
- **Filter by pet**: `Owner.filter_by_pet(pet_name)` — get all tasks for a specific pet (case-insensitive)

### Recurring Task Management
- Daily and weekly tasks automatically create fresh next-occurrence copies when completed
- `Pet.complete_task(task)` marks the task done and appends a new pending instance (daily/weekly only)
- Next occurrence due dates advance by `timedelta(days=1)` or `timedelta(weeks=1)` automatically
- "As needed" tasks do not spawn new instances

### Conflict Detection
- **Same-pet overlaps**: `detect_same_pet_overlaps()` — flags when tasks in a single pet's schedule overlap in time
- **Owner-level overlaps**: `detect_owner_level_overlaps()` — detects when the owner must be in two places simultaneously (e.g., Biscuit's walk overlaps with Mochi's playtime)
- **Category warnings**: Back-to-back tasks in the same category (e.g., two exercise tasks) trigger a rest-break suggestion
- All conflicts are surfaced in the schedule explanation

### Time & Priority Constraints
- Greedy packing algorithm: sorts by priority (high → medium → low), then by shortest-first within each priority tier
- Respects owner's available time budget
- Excludes already-completed and non-matching-day tasks
- Generates human-readable schedule with time windows, priorities, and explanations

See `main.py` for a full demonstration of all features, and `tests/test_pawpal.py` for test coverage (39 tests).

## Testing PawPal+

### Running Tests

```bash
# Run all tests
python -m pytest tests/test_pawpal.py -v

# Run a specific test
python -m pytest tests/test_pawpal.py::test_complete_daily_task_creates_next_occurrence -v
```

### Test Coverage

The test suite includes **39 passing tests** covering:

#### Core Functionality (6 tests)
- Task completion and status tracking
- Pet task management
- Priority-based task sorting (with shortest-first tiebreaker)

#### Task Filtering (7 tests)
- Filtering by completion status (incomplete/completed)
- Filtering by pet name (case-insensitive)
- Filtering by day-of-week (weekly tasks on correct/wrong days)
- Filtering by category
- Excluding completed tasks from schedules

#### Scheduling & Time Management (6 tests)
- Sequential start time assignment
- Time budget enforcement (no overscheduling)
- Task sorting by duration (ascending/descending)
- Conflict detection (back-to-back tasks in same category)

#### Recurring Tasks (5 tests)
- Auto-creation of next occurrences for daily/weekly tasks
- Due date advancement (timedelta)
- No spawning for "as needed" tasks
- Independent copies (mutations don't affect originals)
- Reset behavior for recurring tasks

#### Multi-Pet Support (4 tests)
- Pet persistence in owner's pet list
- Multiple pets in same owner
- Same object reference (mutations visible through owner)
- Task persistence before/after adding to owner

#### Conflict Detection (5 tests)
- Time range overlap detection (edge cases: true/false)
- Same-pet overlaps in schedule
- Owner-level overlaps across multiple pets

### Confidence Level

⭐⭐⭐⭐ (4/5 stars)

**Why 4 stars:**
- ✅ All 39 tests pass consistently
- ✅ Core scheduling logic is well-tested (filtering, sorting, greedy packing)
- ✅ Recurring task management and due dates are verified
- ✅ Conflict detection across single and multiple pets works
- ⚠️ **Minor gaps**:
  - No test for Streamlit UI integration (tested manually via `streamlit run app.py`)
  - No edge cases for extreme values (0 minutes available, 100+ tasks)
  - Due date filtering in scheduler is not yet implemented (only tracked, not enforced)
  - No randomized/fuzz testing

**What would increase confidence to 5 stars:**
- Integration tests for the Streamlit UI
- Edge case testing (empty inputs, very large schedules)
- Implementing due-date-based filtering in the scheduler
- Property-based testing with Hypothesis
