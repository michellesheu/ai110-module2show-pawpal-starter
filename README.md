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

## 📸 Demo

Here's what the final PawPal+ app looks like:

<a href="/course_images/ai110/pawpal_app_screenshot.jpg" target="_blank">
<img src="/course_images/ai110/pawpal_app_screenshot.jpg" alt="PawPal+ Streamlit App Screenshot" width="800" />
</a>

**Key UI Features Shown:**

- ✅ Owner info panel (name, available time)
- ✅ Multi-pet registration and selector
- ✅ Task management with tabs (All / By Duration / By Status)
- ✅ Priority-based color coding (🔴 HIGH, 🟡 MEDIUM, 🟢 LOW)
- ✅ Generated schedule with time windows
- ✅ Conflict warnings and skipped tasks
- ✅ Responsive Streamlit layout (wide mode, tabs, expanders)

**Run the app:**

```bash
streamlit run app.py
```

---

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

## Algorithms Implemented

### 1. Greedy Task Packing with Priority Sorting

**Problem:** Schedule as many high-priority tasks as possible within a time budget.

**Algorithm:**

- Sort tasks by (priority rank, duration) tuple
  - Priority: high (0) → medium (1) → low (2)
  - Duration: shortest-first (SJF tiebreaker within same priority)
- Greedily select tasks in order if they fit in remaining time
- Time complexity: O(n log n) for sorting + O(n) for greedy packing

**Implementation:** `Scheduler.sort_by_priority()` + `filter_by_time()`

**Example:** With 60 minutes available and tasks {Walk: 30m high, Feed: 10m high, Play: 20m medium, Groom: 15m medium}:

1. Sort → [Feed (10m), Walk (30m), Play (20m), Groom (15m)]
2. Select Feed (10m, total 10m)
3. Select Walk (30m, total 40m)
4. Skip Play (20m would exceed 60m)
5. Select Groom (15m, total 55m)
6. Result: Feed, Walk, Groom (55m scheduled)

---

### 2. Interval Overlap Detection

**Problem:** Detect if two time intervals overlap (useful for scheduling conflicts).

**Algorithm:**

- Two intervals [s1, e1) and [s2, e2) overlap if: `s1 < e2 AND s2 < e1`
- Time complexity: O(1) per pair comparison

**Implementation:** `Scheduler._ranges_overlap()` (static helper)

**Used for:**

- Single-pet overlaps: O(n²) all-pairs check within one pet's schedule
- Multi-pet overlaps: O(m² × n²) all-pairs check across all pets (m=pets, n=tasks per pet)

**Example:**

- [0, 10) vs [5, 15) → overlap (0 < 15 AND 5 < 10 ✓)
- [0, 10) vs [10, 20) → no overlap (0 < 20 ✓ but 10 < 10 ✗)

---

### 3. Recurring Task Auto-Creation with Date Arithmetic

**Problem:** When a daily/weekly task is completed, automatically create the next occurrence with an updated due date.

**Algorithm:**

- Use Python's `dataclasses.replace()` to clone task with `completed=False`
- Compute next due date: `base_date + timedelta(days=1)` or `timedelta(weeks=1)`
- Only for tasks with frequency in ("daily", "weekly"); skip "as needed"

**Implementation:** `Pet.complete_task(task)` → returns new Task or None

**Time complexity:** O(1) for cloning + date arithmetic

**Example:**

```python
# Original task
walk = Task(title="Walk", frequency="daily", due_date=2026-03-29)

# After complete_task(walk)
# walk.completed = True
# new_walk = Task(..., completed=False, due_date=2026-03-30)  # tomorrow
```

---

### 4. Status & Time-Range Filtering

**Problem:** Filter tasks by multiple criteria: completion status, time fit, day-of-week, category.

**Algorithm:**

- Filter operations compose: list comprehension with multiple predicates
- Time fitting: check if `time_used + task.duration <= available_minutes`
- Day matching: skip weekly tasks if `scheduled_day != current_day`
- Status: `task.is_complete() == target_status`

**Implementation:** `Scheduler.filter_by_time()`, `filter_by_status()`

**Time complexity:** O(n) for filtering, can be chained without rework

**Example:** `filter_by_time(60, day_of_week="monday")` returns tasks that:

- Are incomplete
- Fit in 60 minutes total (cumulative)
- Are daily OR (weekly AND scheduled for Monday)
- Excludes completed tasks

---

### 5. Sorting by Multiple Criteria

**Problem:** Order tasks in different ways: by duration, by priority, by status.

**Algorithm:**

- `sort_by_duration(tasks, descending)`: simple lambda sort on duration field
- `sort_by_priority(tasks)`: tuple sort (priority_rank, duration) for stable multi-key sort
- `sort_by_status()`: implicit via filter + implicit ordering (completed last)

**Implementation:** `Scheduler.sort_by_duration()`, `sort_by_priority()`

**Time complexity:** O(n log n) per sort

---

### 6. Task Completion State Management

**Problem:** Track which tasks are done, reset recurring tasks for next day/week, prevent duplicate work.

**Algorithm:**

- `mark_complete()`: set `completed = True` flag
- `is_complete()`: check flag
- `reset_if_recurring()`: if frequency in ("daily", "weekly"), set `completed = False`
- Exclusion: `filter_by_time()` automatically drops completed tasks

**Implementation:** Task methods + Scheduler's `filter_by_time()` predicate

**Time complexity:** O(1) for state checks, O(n) to reset all tasks in a pet's list

---

### 7. Schedule Timeline Construction

**Problem:** Convert ordered task list into a timeline with explicit start/end minute windows.

**Algorithm:**

- Iterate through sorted tasks, maintaining a running `current_minute` counter
- For each task: `start = current_minute`, `end = current_minute + duration`, add to timeline
- Advance counter: `current_minute = end`
- Result: list of dicts with `{"task": Task, "start_minute": int, "end_minute": int}`

**Implementation:** `Scheduler.assign_start_times()`

**Time complexity:** O(n) for one pass

**Example:**

```
Input: [Task("Feed", 10), Task("Walk", 30), Task("Play", 20)]
Output: [
  {"task": ..., "start_minute": 0, "end_minute": 10},
  {"task": ..., "start_minute": 10, "end_minute": 40},
  {"task": ..., "start_minute": 40, "end_minute": 60}
]
```

---

### 8. Multi-Level Conflict Detection

**Problem:** Warn users about scheduling conflicts at two levels.

**Algorithm:**

- **Level 1 (same pet)**: O(n²) all-pairs range overlap check on schedule timeline
- **Level 2 (owner/multi-pet)**:
  1. Generate schedules for all pets (O(m × n log n) total)
  2. Perform O(m²) all-pairs pet comparison
  3. For each pet pair, O(n²) all-pairs task comparison
  4. Total: O(m² × n²)
- Back-to-back category check: O(n) scan for consecutive same-category tasks

**Implementation:** `detect_conflicts()`, `detect_same_pet_overlaps()`, `detect_owner_level_overlaps()`

**Warning types:**

- 🟡 Back-to-back same category → suggest rest break
- 🔴 Time overlap same pet → impossible (pet can't be in two places)
- 🔴 Owner overlap → owner can't be in two places simultaneously

**Testing:** 39 tests cover all filtering, sorting, conflict detection, and recurring task scenarios.

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
