import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet


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
