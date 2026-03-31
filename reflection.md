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

The scheduler considers two constraints: **time budget** (`owner.available_minutes`) and **task priority** (1 = low, 2 = medium, 3 = high). A secondary tiebreaker — shortest duration first — applies only when two tasks share the same priority level.

The decision to rank priority above time efficiency came directly from the domain. A pet care app must guarantee that a feeding or medication task (priority 3) is always attempted before a grooming task (priority 1), even if including the grooming task would produce a more "full" schedule mathematically. Getting the wrong task done on time is worse than leaving a few minutes unused. Time budget is a hard cap — the scheduler never exceeds it — but it is secondary to correctness of care ordering.

Owner preferences beyond priority (preferred task order, pet-specific rules like "senior dog needs rest between walks") were deliberately excluded from this iteration. Adding them would have required either a richer `Task` model or per-pet scheduling rules in `Scheduler`, both of which would complicate the logic before the core greedy algorithm was proven correct. The current design leaves a clear extension point: `_rank_tasks()` is a single private method, so pet-aware sorting can be introduced there without touching `generate_plan()`.

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

AI tools were used across every phase of the project, but with a different role in each:

- **Design phase** — Used chat to stress-test the initial UML before writing any code. Prompts like *"Based on my final implementation, what updates should I make to my initial UML diagram?"* surfaced structural issues (the missing `Pet *-- Task` composition, the incorrect `Pet → Owner` back-reference) that would have been harder to catch once code existed.

- **Implementation phase** — Copilot's inline completions were most effective for method bodies that followed a clear pattern: `filter_tasks`, `sort_by_time`, and the `mark_complete` recurrence logic all benefited from completions that correctly applied `sorted()` with a `lambda` key or `timedelta` arithmetic. The completions reduced keystrokes but, more usefully, surfaced the standard Python idiom immediately so I could evaluate it rather than recall it from memory.

- **Test generation** — Prompting with the full system file and asking for tests covering *sorting correctness*, *recurrence logic*, and *conflict detection* produced structurally correct test scaffolds. However, the specific assertions — particularly what "conflict" means in a budget-based scheduler — required manual refinement (see section 3b).

- **Documentation** — Copilot Chat with `#codebase` was used to draft the Features section of the README. The most effective prompt pattern was *"describe what this method does in one sentence from a user's perspective"* rather than *"summarise this file"*, which tended to produce overly technical output.

The single most useful prompt pattern across all phases was **providing the actual code as context** rather than describing it. Prompts that attached `#file:pawpal_system.py` consistently produced more accurate and relevant output than prompts that described the system in natural language.

**b. Judgment and verification**

When AI generated the conflict detection test, it initially asserted that `generate_plan()` would raise an exception or return a specific error flag when two tasks shared the same `due_date`. That framing assumed the scheduler had an explicit duplicate-time check — it does not. The scheduler's only mechanism is the time budget.

The suggestion was rejected because accepting it would have required adding a new code path to `Scheduler` that did not exist and was not needed for the app's current behavior. Instead, the test was rewritten to reflect what the code *actually does*: when two same-priority tasks together exceed the budget, exactly one is scheduled and one appears in `skipped_tasks`. The test verifies observable behavior rather than an assumed implementation detail.

Verification involved reading `generate_plan()` line by line, tracing the greedy loop with two 20-minute tasks and a 30-minute budget on paper, and confirming the expected counts before writing the assertion. Running `pytest -v` after each draft confirmed the test passed for the right reason — not just that it passed.

---

## 4. Testing and Verification

**a. What you tested**

Five core behaviors were identified by reviewing `pawpal_system.py` directly:

1. **Priority ordering** — `_rank_tasks()` sorts by `(-priority, duration_minutes)`. A priority-3 task must always appear in the plan before a priority-1 task, regardless of insertion order.

2. **Skipped tasks are preserved, not dropped** — `generate_plan()` routes over-budget tasks into `skipped_tasks`. After generating a plan with a tight budget, every task must appear in either `scheduled_tasks` or `skipped_tasks` — none silently lost.

3. **`mark_complete()` returns the correct next occurrence** — A `"daily"` task should return a new task with `due_date = date.today() + timedelta(days=1)`. A `"weekly"` task should return `due_date = date.today() + timedelta(weeks=1)`. An `"as-needed"` task should return `None`.

4. **Completed tasks are excluded from the next plan** — `get_all_pending_tasks()` filters by `not t.is_completed`. After calling `mark_task_complete()`, the original completed task must not appear in a freshly generated `DailyPlan`.

5. **`filter_tasks()` correctly combines both parameters** — When called with `completed=False` and `pet_name="Mochi"`, only Mochi's pending tasks should be returned — not Luna's, and not Mochi's completed tasks. Each parameter should be tested alone and in combination.

These five cover the full task lifecycle: **adding → ranking → scheduling → completing → recurring**.

**b. Confidence**

Confidence level: **4 / 5**. The five implemented tests cover the full task lifecycle — adding, ranking, scheduling, completing, and recurring — and all pass. The greedy algorithm is simple enough that its behavior is easy to reason about manually, which increases confidence beyond what the tests alone provide.

The missing star reflects three untested areas:

1. **Recurrence boundary dates** — A `"weekly"` task completed on Feb 22 should produce `due_date = Mar 1`, not a date 7 calendar days away that accidentally crosses a month boundary incorrectly. The current `timedelta(weeks=1)` handles this correctly in Python, but it has not been tested explicitly.

2. **Completed task exclusion from the next plan** — Section 4a identifies this as a key behavior, but no test currently asserts that a completed task is absent from a freshly generated `DailyPlan`. The logic exists in `get_all_pending_tasks()`, but the integration path through `generate_plan()` is untested end-to-end.

3. **`filter_tasks` with both parameters combined** — Individual parameter tests exist implicitly, but a test asserting that `filter_tasks(completed=False, pet_name="Mochi")` excludes both completed Mochi tasks *and* all Luna tasks simultaneously has not been written.

---

## 5. Reflection

**a. What went well**

The part of this project I am most satisfied with is the **separation between domain logic and the UI**. `pawpal_system.py` has no Streamlit imports and no awareness of how it is displayed. Every scheduling decision — ranking, budget checking, recurrence — lives in Python classes that can be tested, reasoned about, and reused independently of any frontend. This paid off directly when the UI needed to be updated: swapping `st.text(plan.display())` for `st.metric`, `st.table`, and `st.warning` components required zero changes to `pawpal_system.py`. The boundary held cleanly.

The recurrence design is also something I am satisfied with. Returning `Task | None` from `mark_complete()` keeps the logic inside the `Task` class (where the frequency knowledge lives) while letting `Scheduler.mark_task_complete()` decide what to do with the result. This avoided duplicating frequency-checking logic in both the model and the scheduler.

**b. What you would improve**

Two things stand out for a next iteration:

1. **Gap-filling second pass in `generate_plan()`** — As noted in section 2b, the greedy algorithm can leave unused time when a high-priority task doesn't fit but smaller lower-priority tasks would. A second pass over `skipped_tasks` after the main loop — inserting any task that fits the remaining budget without displacing already-scheduled tasks — would produce fuller schedules without changing the priority guarantee.

2. **`TaskManager` integration** — `TaskManager` was designed as a standalone utility but is never wired into `Scheduler` or the Streamlit UI. In the current app, task management is done directly through `Pet.add_task()`. Either `TaskManager` should be connected to the owner/pet model as the single source of task mutations, or it should be removed to avoid confusion about which path to use. The current state — two separate mutation paths — is the kind of silent inconsistency that causes bugs later.

**c. Key takeaway**

The most important thing I learned is that **AI tools are most valuable when you already have a structure to evaluate their output against**. When I had a UML diagram, I could look at an AI-generated method signature and immediately judge whether it fit the design or violated a relationship. When I had a test suite, I could accept or reject a suggested assertion by tracing what the code actually does. Without those anchors, AI suggestions are hard to evaluate — they sound plausible but there is no frame to check them against.

This is what it means to be the lead architect in an AI-assisted project. The AI accelerates every phase — drafting, completing, generating, explaining — but it cannot set the direction, catch a design inconsistency it was not asked about, or know that a suggested addition would duplicate a responsibility that already exists elsewhere. That judgment belongs to the human. The right workflow is: design first, then use AI to execute faster within that design, then verify that the output still respects the design. Skipping the first step does not save time — it defers the design work until the code is harder to change.
