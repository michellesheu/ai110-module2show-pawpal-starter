# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
add a pet, schedule a walk, see today's tasks)

- Briefly describe your initial UML design.
  My initial UML design consists of four classes: Pet, Task, Owner, and Scheduler. The Pet class stores the pet's attributes and belongs to an Owner. The Task class represents pet care activities such as walking, feeding, medications, and enrichment. The Owner class holds the owner's schedule and constraints, such as how much time is available each day. The Scheduler class will generate a plan based on the owner's and their pet's information.

- What classes did you include, and what responsibilities did you assign to each?
  The design includes four classes. The Owner class is responsible for storing the owner's name and daily time constraints, representing the limits within which the schedule must fit. The Pet class is responsible for storing the pet's name, species, and age, and is associated with its Owner. The Task class is responsible for representing a single care activity, holding attributes like title, duration in minutes, priority, and category so the scheduler can select and order tasks appropriately. The Scheduler class is responsible for generating a schedule which takes the Owner and Pet as input.

**b. Design changes**

- Did your design change during implementation?
  Yes, the design changed during implementation.

- If yes, describe at least one change and why you made it.
  The original UML showed the Scheduler with a separate `available_tasks` list, but during implementation I realized the Scheduler should pull tasks directly from the Pet object it already holds rather than maintaining a disconnected list. I also added a `scheduled_tasks` attribute to store the result of `generate_schedule()`, because without it `explain_schedule()` had no way to access the final schedule it needed to describe. These changes were necessary because the original design had no clear data flow from Pet → Scheduler → explanation output.

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
