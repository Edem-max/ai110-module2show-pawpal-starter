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

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
