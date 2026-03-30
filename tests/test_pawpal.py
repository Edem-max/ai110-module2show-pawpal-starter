import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


def test_mark_complete_changes_status():
    """Task.mark_complete() should flip is_completed from False to True."""
    task = Task("t1", "Morning Walk", "exercise", 30, priority=3)
    assert task.is_completed is False

    task.mark_complete()

    assert task.is_completed is True


def test_add_task_increases_pet_task_count():
    """Pet.add_task() should increase the pet's task list by one."""
    pet = Pet("Mochi", "dog", 3)
    assert len(pet.tasks) == 0

    pet.add_task(Task("t2", "Breakfast", "feeding", 10, priority=3))

    assert len(pet.tasks) == 1


# --- Sorting correctness ---

def test_sort_by_time_returns_chronological_order():
    """Scheduler.sort_by_time() should return tasks shortest-duration first."""
    owner = Owner("Alex", available_minutes=120)
    pet = Pet("Mochi", "dog", 3)
    owner.add_pet(pet)

    pet.add_task(Task("t3", "Evening Walk", "exercise", 45, priority=2))
    pet.add_task(Task("t4", "Brush Teeth", "grooming", 5, priority=1))
    pet.add_task(Task("t5", "Lunch", "feeding", 20, priority=3))

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time()

    durations = [t.duration_minutes for t in sorted_tasks]
    assert durations == sorted(durations), (
        f"Expected ascending order, got {durations}"
    )


# --- Recurrence logic ---

def test_daily_task_creates_next_occurrence_on_complete():
    """Completing a daily task via Scheduler should add a new task due tomorrow."""
    owner = Owner("Alex", available_minutes=120)
    pet = Pet("Mochi", "dog", 3)
    owner.add_pet(pet)

    task = Task("t6", "Morning Walk", "exercise", 30, priority=3, frequency="daily")
    pet.add_task(task)

    scheduler = Scheduler(owner)
    scheduler.mark_task_complete("Mochi", "t6")

    assert task.is_completed is True
    assert len(pet.tasks) == 2, "A new recurring task should have been appended"

    next_task = pet.tasks[1]
    assert next_task.is_completed is False
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert next_task.name == task.name
    assert next_task.frequency == "daily"


# --- Conflict detection ---

def test_scheduler_flags_duplicate_due_times():
    """Scheduler.generate_plan() should not schedule two tasks with identical due dates
    when the budget only fits one; the second must appear in skipped_tasks."""
    owner = Owner("Alex", available_minutes=30)
    pet = Pet("Mochi", "dog", 3)
    owner.add_pet(pet)

    today = date.today()
    pet.add_task(Task("t7", "Feeding A", "feeding", 20, priority=3, due_date=today))
    pet.add_task(Task("t8", "Feeding B", "feeding", 20, priority=3, due_date=today))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    assert len(plan.scheduled_tasks) == 1, (
        "Only one task should fit within the 30-minute budget"
    )
    assert len(plan.skipped_tasks) == 1, (
        "The conflicting same-time task should be flagged as skipped"
    )
