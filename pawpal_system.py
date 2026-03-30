from dataclasses import dataclass, field


@dataclass
class Owner:
    name: str
    available_minutes: int

    def update_availability(self, _minutes: int) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    owner: Owner

    def get_summary(self) -> str:
        pass


@dataclass
class Task:
    task_id: str
    name: str
    category: str
    duration_minutes: int
    priority: int
    is_completed: bool = False

    def mark_complete(self) -> None:
        pass

    def to_dict(self) -> dict:
        pass


class TaskManager:
    def __init__(self):
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task_id: str) -> None:
        pass

    def edit_task(self, task_id: str, **changes) -> None:
        pass

    def get_all_tasks(self) -> list[Task]:
        pass

    def get_by_priority(self) -> list[Task]:
        pass


class Scheduler:
    def __init__(self, owner: Owner, task_manager: TaskManager):
        self.owner = owner
        self.task_manager = task_manager

    def generate_plan(self) -> "DailyPlan":
        pass

    def _fits_in_budget(self, tasks: list[Task]) -> bool:
        pass

    def _rank_tasks(self) -> list[Task]:
        pass


@dataclass
class DailyPlan:
    scheduled_tasks: list[Task] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    total_duration: int = 0
    reasoning: str = ""

    def display(self) -> str:
        pass

    def to_dict(self) -> dict:
        pass
