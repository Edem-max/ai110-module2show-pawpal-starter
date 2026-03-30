import uuid
from dataclasses import dataclass, field
from datetime import date, timedelta


@dataclass
class Task:
    """A single pet care activity."""
    task_id: str
    name: str
    category: str          # e.g. "exercise", "feeding", "grooming"
    duration_minutes: int
    priority: int          # 1 = low, 2 = medium, 3 = high
    frequency: str = "daily"   # e.g. "daily", "weekly", "as-needed"
    is_completed: bool = False
    due_date: date | None = None

    def mark_complete(self) -> "Task | None":
        """Mark this task as completed and return the next occurrence, or None."""
        self.is_completed = True

        if self.frequency == "daily":
            next_due = date.today() + timedelta(days=1)
        elif self.frequency == "weekly":
            next_due = date.today() + timedelta(weeks=1)
        else:
            return None

        return Task(
            task_id=uuid.uuid4().hex[:6],
            name=self.name,
            category=self.category,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            is_completed=False,
            due_date=next_due,
        )

    def to_dict(self) -> dict:
        """Return a plain-dictionary representation of this task."""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "category": self.category,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "frequency": self.frequency,
            "is_completed": self.is_completed,
            "due_date": str(self.due_date) if self.due_date else None,
        }


@dataclass
class Pet:
    """A pet and its associated care tasks."""
    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove the task with the given ID from this pet's task list."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def get_pending_tasks(self) -> list[Task]:
        """Return all tasks that have not yet been completed."""
        return [t for t in self.tasks if not t.is_completed]

    def get_summary(self) -> str:
        """Return a one-line description of the pet and its task counts."""
        pending = len(self.get_pending_tasks())
        total = len(self.tasks)
        return (
            f"{self.name} ({self.species}, age {self.age}) — "
            f"{total} task(s) total, {pending} pending"
        )


@dataclass
class Owner:
    """An owner who manages one or more pets."""
    name: str
    available_minutes: int
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove the pet with the given name from this owner's roster."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def update_availability(self, minutes: int) -> None:
        """Update the number of minutes the owner has available today."""
        self.available_minutes = minutes

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all pets."""
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks

    def get_all_pending_tasks(self) -> list[Task]:
        """Return only incomplete tasks across all pets."""
        return [t for t in self.get_all_tasks() if not t.is_completed]


class TaskManager:
    """Utility for bulk task operations on a flat task list."""

    def __init__(self) -> None:
        """Initialize an empty task list."""
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a task to the managed list."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a task by its ID."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def edit_task(self, task_id: str, **changes) -> None:
        """Update one or more fields on the task with the given ID."""
        for task in self.tasks:
            if task.task_id == task_id:
                for attr, value in changes.items():
                    if hasattr(task, attr):
                        setattr(task, attr, value)
                return
        raise ValueError(f"Task '{task_id}' not found.")

    def get_all_tasks(self) -> list[Task]:
        """Return a copy of the full task list."""
        return list(self.tasks)

    def get_by_priority(self) -> list[Task]:
        """Return tasks sorted highest priority first."""
        return sorted(self.tasks, key=lambda t: t.priority, reverse=True)


class Scheduler:
    """The brain: builds a time-budgeted daily plan across all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        """Bind the scheduler to a specific owner."""
        self.owner = owner

    def _rank_tasks(self) -> list[Task]:
        """Sort all pending tasks by priority (high → low), then shortest first as tiebreak."""
        pending = self.owner.get_all_pending_tasks()
        return sorted(pending, key=lambda t: (-t.priority, t.duration_minutes))

    def _fits_in_budget(self, task: Task, minutes_used: int) -> bool:
        """Return True if adding this task stays within the owner's time budget."""
        return minutes_used + task.duration_minutes <= self.owner.available_minutes

    def sort_by_time(self, tasks: list[Task] | None = None, reverse: bool = False) -> list[Task]:
        """Return tasks sorted by duration_minutes, shortest first by default.

        Uses a lambda key on ``task.duration_minutes`` so Python's built-in
        ``sorted()`` can compare tasks numerically rather than by object identity.

        Args:
            tasks:   An explicit list of tasks to sort. If omitted, all pending
                     tasks across the owner's pets are used.
            reverse: When False (default) the shortest task appears first, which
                     maximises how many tasks fit within the owner's time budget.
                     When True the longest task appears first.

        Returns:
            A new sorted list; the original list (or pet task lists) are unchanged.
        """
        source = tasks if tasks is not None else self.owner.get_all_pending_tasks()
        return sorted(source, key=lambda t: t.duration_minutes, reverse=reverse)

    def filter_tasks(
        self,
        completed: bool | None = None,
        pet_name: str | None = None,
    ) -> list[Task]:
        """Return tasks filtered by completion status and/or pet name.

        Args:
            completed: If True, return only completed tasks. If False, return only
                       pending tasks. If None, return tasks regardless of status.
            pet_name:  If given, return only tasks belonging to that pet.
                       If None, return tasks across all pets.
        """
        results: list[Task] = []
        for pet in self.owner.pets:
            if pet_name is not None and pet.name != pet_name:
                continue
            for task in pet.tasks:
                if completed is not None and task.is_completed != completed:
                    continue
                results.append(task)
        return results

    def mark_task_complete(self, pet_name: str, task_id: str) -> None:
        """Mark a task complete and auto-schedule the next occurrence if recurring.

        Delegates to ``Task.mark_complete()``, which returns a new ``Task`` whose
        ``due_date`` is calculated with ``timedelta`` (``days=1`` for daily tasks,
        ``weeks=1`` for weekly tasks). If a next task is produced it is appended
        directly to the pet's task list so it will appear in the next generated plan.

        Args:
            pet_name: The name of the pet whose task should be completed.
                      No-ops silently if the pet is not found.
            task_id:  The ID of the task to mark complete.
                      No-ops silently if the task is not found on that pet.
        """
        pet = next((p for p in self.owner.pets if p.name == pet_name), None)
        if pet is None:
            return
        task = next((t for t in pet.tasks if t.task_id == task_id), None)
        if task is None:
            return
        next_task = task.mark_complete()
        if next_task is not None:
            pet.add_task(next_task)

    def generate_plan(self) -> "DailyPlan":
        """Build and return a DailyPlan using the owner's available time and pet tasks."""
        ranked = self._rank_tasks()
        plan = DailyPlan()
        minutes_used = 0

        for task in ranked:
            if self._fits_in_budget(task, minutes_used):
                plan.scheduled_tasks.append(task)
                minutes_used += task.duration_minutes
            else:
                plan.skipped_tasks.append(task)

        plan.total_duration = minutes_used
        plan.reasoning = (
            f"Scheduled {len(plan.scheduled_tasks)} task(s) for {self.owner.name} "
            f"using {minutes_used} of {self.owner.available_minutes} available minute(s). "
            f"Skipped {len(plan.skipped_tasks)} task(s) due to time constraints."
        )
        return plan


@dataclass
class DailyPlan:
    scheduled_tasks: list[Task] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    total_duration: int = 0
    reasoning: str = ""
    plan_date: date = field(default_factory=date.today)

    def display(self) -> str:
        """Return a formatted string showing the full daily plan."""
        lines = [f"=== Daily Plan ({self.plan_date}) ==="]

        if self.scheduled_tasks:
            lines.append("\nScheduled tasks:")
            for i, task in enumerate(self.scheduled_tasks, 1):
                status = "✓" if task.is_completed else "○"
                lines.append(
                    f"  {i}. [{status}] {task.name} "
                    f"({task.category}, {task.duration_minutes} min, priority {task.priority})"
                )
        else:
            lines.append("\nNo tasks scheduled.")

        if self.skipped_tasks:
            lines.append("\nSkipped (insufficient time):")
            for task in self.skipped_tasks:
                lines.append(f"  - {task.name} ({task.duration_minutes} min)")

        lines.append(f"\nTotal time: {self.total_duration} min")
        lines.append(f"\nReasoning: {self.reasoning}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Return a serializable dictionary representation of this plan."""
        return {
            "plan_date": str(self.plan_date),
            "total_duration": self.total_duration,
            "reasoning": self.reasoning,
            "scheduled_tasks": [t.to_dict() for t in self.scheduled_tasks],
            "skipped_tasks": [t.to_dict() for t in self.skipped_tasks],
        }
