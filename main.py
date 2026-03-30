from pawpal_system import Task, Pet, Owner, Scheduler


def main():
    # --- Create Owner ---
    jordan = Owner("Jordan", available_minutes=90)

    # --- Create Pets ---
    mochi = Pet("Mochi", "dog", 3)
    luna = Pet("Luna", "cat", 5)

    # --- Add Tasks to Mochi ---
    mochi.add_task(Task("t1", "Morning Walk",  "exercise", 30, priority=3, frequency="daily"))
    mochi.add_task(Task("t2", "Breakfast",     "feeding",  10, priority=3, frequency="daily"))
    mochi.add_task(Task("t3", "Brushing",      "grooming", 20, priority=2, frequency="weekly"))

    # --- Add Tasks to Luna ---
    luna.add_task(Task("t4", "Playtime",       "exercise", 25, priority=2, frequency="daily"))
    luna.add_task(Task("t5", "Bath",           "grooming", 45, priority=1, frequency="weekly"))

    # --- Register Pets with Owner ---
    jordan.add_pet(mochi)
    jordan.add_pet(luna)

    # --- Print Today's Schedule ---
    print("========================================")
    print("         TODAY'S SCHEDULE               ")
    print("========================================")
    print(f"Owner : {jordan.name}")
    print(f"Budget: {jordan.available_minutes} minutes\n")

    print("Pets:")
    for pet in jordan.pets:
        print(f"  {pet.get_summary()}")

    print()
    scheduler = Scheduler(jordan)
    plan = scheduler.generate_plan()
    print(plan.display())
    print("========================================")


if __name__ == "__main__":
    main()
