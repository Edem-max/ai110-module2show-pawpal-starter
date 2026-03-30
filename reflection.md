# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The initial UML design centers on six classes: `Owner`, `Pet`, `Task`, `TaskManager`, `Scheduler`, and `DailyPlan`.

- `Owner` holds the pet owner's name and daily available time, which the scheduler uses as a hard constraint.
- `Pet` stores basic pet info (name, species, age) and is linked to the owner.
- `Task` represents a single care activity with a name, category, duration in minutes, and a priority level (1–5).
- `TaskManager` handles adding, editing, and removing tasks — keeping data management separate from planning logic.
- `Scheduler` takes the owner's constraints and the task list, then selects and orders tasks that fit within the available time.
- `DailyPlan` stores the final scheduled tasks, total duration, and a plain-language explanation of why each task was included or skipped.

**Three core actions a user can perform:**

1. **Add a pet and owner profile** — The user enters their name, their pet's name/species, and how many minutes per day they have available. This sets the constraints the scheduler will use when building the plan.

2. **Add and manage care tasks** — The user creates tasks like "morning walk" (30 min, priority 5) or "flea treatment" (10 min, priority 3). They can edit duration and priority, or remove tasks that no longer apply.

3. **Generate and view today's daily plan** — The user triggers the scheduler, which selects tasks by priority and fits them within the available time. The app displays the scheduled tasks in order and explains why certain tasks were included or left out.

**b. Design changes**

Yes, the design changed in three ways after reviewing the skeleton with AI feedback:

1. **`Scheduler` now holds a `Pet` reference** — In the original design, `Pet` was linked to `Owner` but never reached the `Scheduler`. This meant pet-specific context (species, age) was unavailable during planning. Adding `pet` as a direct parameter to `Scheduler.__init__` keeps the door open for pet-aware scheduling rules (e.g. senior dogs need shorter walks) without breaking the current logic.

2. **`_fits_in_budget` signature changed from `(tasks: list[Task])` to `(task: Task, minutes_used: int)`** — The original signature encouraged checking an already-built list, which would require building the plan twice. The new signature supports a greedy loop in `generate_plan`: iterate ranked tasks one at a time, check if the next task fits within remaining budget, and add or skip accordingly. This is a more natural and efficient scheduling pattern.

3. **`DailyPlan` gained a `plan_date` field** — Without a date, every generated plan looks identical in storage. Adding `plan_date: date` (defaulting to today) makes plans distinguishable and lays the groundwork for history or streak tracking later.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

The scheduler uses a **greedy first-fit algorithm**: it iterates through tasks ranked by priority and adds each one if its duration fits within the remaining time budget. It never looks ahead or backtracks.

This means it can leave time on the table. For example, if the owner has 25 minutes left and the next task needs 30 minutes, that task is skipped — even if two smaller tasks totaling 20 minutes are waiting further down the list and would fit comfortably. The schedule is built by checking cumulative duration against `available_minutes`, not by finding the combination of tasks that fills the budget most efficiently.

This tradeoff is reasonable for a daily pet care app because:

1. **Simplicity over optimality** — A pet owner generating a morning routine does not need a mathematically perfect schedule. They need a fast, predictable result that respects their highest-priority tasks first.
2. **Priority is the primary constraint** — Missing a high-priority task (medication, feeding) to squeeze in a low-priority one (grooming) would be the wrong outcome even if it used more minutes. The greedy approach guarantees high-priority tasks are always considered first.
3. **The cost of suboptimality is low** — Leaving 25 minutes unused is a minor inconvenience, not a correctness failure. The skipped tasks are surfaced in `DailyPlan.skipped_tasks`, so the owner can reschedule them manually.

A future improvement would be a gap-filling second pass: after the main greedy loop completes, iterate over `skipped_tasks` once more and slot in any that fit the remaining minutes, without reordering priority-selected tasks.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
