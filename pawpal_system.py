from dataclasses import dataclass, field
from datetime import date


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

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True

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
