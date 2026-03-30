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

## Smarter Scheduling

Three algorithmic improvements were added to `Scheduler` in `pawpal_system.py` to make the daily plan more useful for a real pet owner.

**Sort by duration (`sort_by_time`)**
Tasks can be ordered by how long they take — shortest first by default, longest first with `reverse=True`. The sort uses a `lambda` key on `task.duration_minutes` so Python's built-in `sorted()` compares tasks numerically. Sorting shortest-first helps maximise how many tasks fit within the owner's available time.

**Filter by status or pet (`filter_tasks`)**
Returns a subset of tasks matching any combination of:
- `completed=True` / `False` — isolate done or pending tasks
- `pet_name="Mochi"` — scope results to a single pet

Both parameters are optional and composable (e.g. "Luna's pending tasks only").

**Auto-reschedule recurring tasks (`mark_task_complete`)**
When a `"daily"` or `"weekly"` task is marked complete, a new instance is automatically created for the next occurrence. The next due date is calculated with Python's `timedelta`:
- `"daily"` → `date.today() + timedelta(days=1)`
- `"weekly"` → `date.today() + timedelta(weeks=1)`
- `"as-needed"` → no new task created

The new task is appended to the pet's task list immediately and will appear in the next generated plan.

---

## Testing PawPal+

### Run the test suite

```bash
python3 -m pytest tests/test_pawpal.py -v
```

### What the tests cover

| Test | Area | Description |
|---|---|---|
| `test_mark_complete_changes_status` | Task state | `mark_complete()` flips `is_completed` from `False` to `True` |
| `test_add_task_increases_pet_task_count` | Pet management | `Pet.add_task()` grows the task list by one |
| `test_sort_by_time_returns_chronological_order` | **Sorting** | `Scheduler.sort_by_time()` returns tasks in ascending duration order |
| `test_daily_task_creates_next_occurrence_on_complete` | **Recurrence** | Completing a `daily` task appends a new task due tomorrow |
| `test_scheduler_flags_duplicate_due_times` | **Conflict detection** | Two same-priority tasks at the same time respect the budget; the second is skipped |

### Confidence Level

**4 / 5 stars**

The core scheduling behaviors — sorting, recurrence, and conflict handling — are verified and all 5 tests pass. One star is withheld because the conflict detection test exercises budget overflow as a proxy for duplicate-time flagging (the scheduler has no explicit duplicate-time check), and edge cases like DST transitions, leap-year recurrence, and concurrent edits are not yet covered.

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
