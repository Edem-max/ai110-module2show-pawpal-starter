from pawpal_system import Task, Pet, Owner, Scheduler


def main():
    # --- Create Owner ---
    jordan = Owner("Jordan", available_minutes=90)

    # --- Create Pets ---
    mochi = Pet("Mochi", "dog", 3)
    luna = Pet("Luna", "cat", 5)

    # --- Add Tasks OUT OF ORDER (mixed priorities and durations) ---
    mochi.add_task(Task("t3", "Brushing",      "grooming", 20, priority=2, frequency="weekly"))
    mochi.add_task(Task("t1", "Morning Walk",  "exercise", 30, priority=3, frequency="daily"))
    mochi.add_task(Task("t2", "Breakfast",     "feeding",  10, priority=3, frequency="daily"))

    luna.add_task(Task("t5", "Bath",           "grooming", 45, priority=1, frequency="weekly"))
    luna.add_task(Task("t4", "Playtime",       "exercise", 25, priority=2, frequency="daily"))

    # Mark one task complete to demonstrate filtering
    mochi.tasks[0].mark_complete()   # Brushing is done

    # --- Register Pets with Owner ---
    jordan.add_pet(mochi)
    jordan.add_pet(luna)

    scheduler = Scheduler(jordan)

    # ----------------------------------------------------------------
    # 1. Sort all pending tasks by duration (shortest → longest)
    # ----------------------------------------------------------------
    print("========================================")
    print("  SORTED BY DURATION (shortest first)  ")
    print("========================================")
    for task in scheduler.sort_by_time():
        print(f"  {task.duration_minutes:>3} min  |  {task.name}")

    print()
    print("========================================")
    print("  SORTED BY DURATION (longest first)   ")
    print("========================================")
    for task in scheduler.sort_by_time(reverse=True):
        print(f"  {task.duration_minutes:>3} min  |  {task.name}")

    # ----------------------------------------------------------------
    # 2. Filter: completed tasks only (across all pets)
    # ----------------------------------------------------------------
    print()
    print("========================================")
    print("  FILTER: completed tasks               ")
    print("========================================")
    done = scheduler.filter_tasks(completed=True)
    if done:
        for task in done:
            print(f"  [✓] {task.name}")
    else:
        print("  (none)")

    # ----------------------------------------------------------------
    # 3. Filter: pending tasks only (across all pets)
    # ----------------------------------------------------------------
    print()
    print("========================================")
    print("  FILTER: pending tasks                 ")
    print("========================================")
    for task in scheduler.filter_tasks(completed=False):
        print(f"  [○] {task.name}")

    # ----------------------------------------------------------------
    # 4. Filter: all tasks for a specific pet
    # ----------------------------------------------------------------
    print()
    print("========================================")
    print("  FILTER: Mochi's tasks only            ")
    print("========================================")
    for task in scheduler.filter_tasks(pet_name="Mochi"):
        status = "✓" if task.is_completed else "○"
        print(f"  [{status}] {task.name}  ({task.duration_minutes} min)")

    # ----------------------------------------------------------------
    # 5. Filter: pending tasks for a specific pet
    # ----------------------------------------------------------------
    print()
    print("========================================")
    print("  FILTER: Luna's pending tasks          ")
    print("========================================")
    for task in scheduler.filter_tasks(completed=False, pet_name="Luna"):
        print(f"  [○] {task.name}  ({task.duration_minutes} min)")

    # ----------------------------------------------------------------
    # 6. Full generated schedule
    # ----------------------------------------------------------------
    print()
    print("========================================")
    print("         TODAY'S SCHEDULE               ")
    print("========================================")
    plan = scheduler.generate_plan()
    print(plan.display())
    print("========================================")

    # ----------------------------------------------------------------
    # 7. Mark a recurring task complete — auto-creates next occurrence
    # ----------------------------------------------------------------
    print()
    print("========================================")
    print("  RECURRING TASK DEMO: mark t2 complete ")
    print("========================================")

    print("\nMochi's tasks BEFORE completing Breakfast (t2):")
    for task in mochi.tasks:
        status = "✓" if task.is_completed else "○"
        print(f"  [{status}] [{task.task_id}] {task.name}  (due: {task.due_date})")

    scheduler.mark_task_complete("Mochi", "t2")

    print("\nMochi's tasks AFTER completing Breakfast (t2):")
    for task in mochi.tasks:
        status = "✓" if task.is_completed else "○"
        print(f"  [{status}] [{task.task_id}] {task.name}  (due: {task.due_date})")

    # Show the newly created next-occurrence task
    new_breakfast = next(
        (t for t in mochi.tasks if t.name == "Breakfast" and not t.is_completed),
        None,
    )
    if new_breakfast:
        print(f"\nNext Breakfast auto-scheduled:")
        print(f"  task_id : {new_breakfast.task_id}")
        print(f"  due_date: {new_breakfast.due_date}")
    print("========================================")


if __name__ == "__main__":
    main()
