# PawPal+

> A smart pet-care scheduling assistant built with Python and Streamlit.
> PawPal+ helps busy pet owners plan daily care tasks across multiple pets,
> respecting time budgets, task priorities, and recurring schedules.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Getting Started](#getting-started)
5. [Running the App](#running-the-app)
6. [Testing PawPal+](#testing-pawpal)
7. [UML Class Diagram](#uml-class-diagram)

---

## Overview

A busy pet owner needs help staying consistent with pet care. PawPal+ lets them:

- Register an owner profile with a daily time budget
- Add one or more pets with their own task lists
- Build a prioritised daily plan that fits within available time
- Track recurring tasks that automatically reschedule after completion
- See real-time conflict warnings when tasks exceed the time budget

---

## Features

### Scheduling Algorithm
PawPal+ uses a **greedy priority scheduler** (`Scheduler.generate_plan`) that:
1. Collects all pending tasks across every pet owned by the user
2. Sorts them by priority (high → low), using shortest duration as a tiebreaker
3. Greedily adds tasks to the plan until the owner's available minutes are used up
4. Any task that no longer fits is placed in a **skipped tasks** list with an explanation

### Sorting by Time (`sort_by_time`)
Tasks can be displayed in duration order using a `lambda` key on `task.duration_minutes`
passed to Python's built-in `sorted()`. Shortest-first is the default, which maximises
how many tasks fit in the owner's time budget. Pass `reverse=True` to show longest first.

### Conflict Warnings
When the total duration of all pending tasks exceeds the owner's available minutes,
the UI immediately shows an `st.warning` banner with the exact overflow in minutes.
This surfaces the conflict **before** the plan is generated, giving the owner a chance
to adjust priorities or free up time. At plan generation time, overflowing tasks are
moved to `DailyPlan.skipped_tasks` and listed separately in the UI.

### Daily Recurrence (`mark_task_complete`)
Marking a `"daily"` or `"weekly"` task complete via `Scheduler.mark_task_complete()`
automatically creates the next occurrence using Python's `timedelta`:

| Frequency | Next due date |
|-----------|--------------|
| `"daily"` | `date.today() + timedelta(days=1)` |
| `"weekly"` | `date.today() + timedelta(weeks=1)` |
| `"as-needed"` | No new task created |

The new task is appended directly to the pet's task list and will appear in tomorrow's plan.

### Filtering (`filter_tasks`)
`Scheduler.filter_tasks()` returns a scoped subset of tasks. Both parameters are optional
and composable:

- `completed=True / False` — isolate done or pending tasks
- `pet_name="Mochi"` — restrict results to a single pet

Example: `filter_tasks(completed=False, pet_name="Luna")` returns only Luna's pending tasks.

### Priority-Based Bulk Sorting (`TaskManager.get_by_priority`)
`TaskManager` provides a standalone utility for sorting any flat task list by priority
(highest first) independently of the scheduler, useful for displaying task backlogs.

---

## Project Structure

```
pawpal_system.py   — Core domain classes: Task, Pet, Owner, Scheduler,
                     TaskManager, DailyPlan
app.py             — Streamlit UI: owner setup, pet/task entry, plan display
tests/
  test_pawpal.py   — pytest suite covering sorting, recurrence, and conflicts
uml_diagram.puml   — PlantUML source for the class diagram
uml_diagram.mmd    — Mermaid source (paste into mermaid.live to render)
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## Running the App

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

**Workflow:**

1. Enter your name and available minutes, then click **Save owner**
2. Add one or more pets with **Add pet**
3. Add care tasks (title, duration, priority, pet) with **Add task**
4. Watch the conflict warning appear if your tasks exceed your time budget
5. Click **Generate schedule** to build the daily plan

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

The core scheduling behaviors — sorting, recurrence, and conflict handling — are verified
and all 5 tests pass. One star is withheld because conflict detection exercises budget
overflow as a proxy (no explicit duplicate-time check exists), and edge cases like DST
transitions, leap-year recurrence, and concurrent edits are not yet covered.
<img width="5791" height="3248" alt="mermaid-diagram-2026-03-31-020203" src="https://github.com/user-attachments/assets/126d5192-5b2f-4513-b25c-d842bf97fa0b" />

---

## UML Class Diagram

The updated class diagram is available in two formats:

- **PlantUML** — open `uml_diagram.puml` or paste into [planttext.com](https://www.planttext.com)
- **Mermaid** — open `uml_diagram.mmd` or paste into [mermaid.live](https://mermaid.live)

Key design decisions reflected in the diagram:

- `Owner *-- Pet *-- Task` — composition chain; tasks live inside pets, pets live inside the owner
- `Scheduler` holds a reference to `Owner` (association), not ownership
- `Scheduler ..> DailyPlan` — dependency; `generate_plan()` creates and returns a new plan each call
- `Task ..> Task` — self-dependency; `mark_complete()` produces the next recurring instance
