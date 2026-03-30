import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("🐾 PawPal+")
st.markdown("A pet care planning assistant that helps you schedule daily tasks based on priority and time constraints.")

st.divider()

# ── Initialize session state ──────────────────────────────────────

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=60, pets=[])

# ── Owner Info Section ────────────────────────────────────────────

col1, col2 = st.columns(2)

with col1:
    st.subheader("Owner Info")
    owner_name = st.text_input("Owner name", value=st.session_state.owner.name)
    available_time = st.number_input(
        "Available time (minutes)",
        min_value=1,
        max_value=480,
        value=st.session_state.owner.available_minutes
    )

with col2:
    st.subheader("")
    st.write("")  # spacing
    if st.button("💾 Save owner info", use_container_width=True):
        st.session_state.owner.name = owner_name
        st.session_state.owner.available_minutes = int(available_time)
        st.success(f"✓ Owner info saved for **{owner_name}** ({available_time} min/day)")

st.divider()

# ── Pet Management ────────────────────────────────────────────────

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.subheader("Add a Pet")
    pet_name = st.text_input("Pet name", value="Mochi", key="pet_input")

with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"], key="species_select")

with col3:
    pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=3, key="age_input")

col1, col2 = st.columns(2)
with col1:
    if st.button("➕ Add pet", use_container_width=True):
        existing_names = [p.get_name().lower() for p in st.session_state.owner.get_pets()]
        if pet_name.lower() in existing_names:
            st.error(f"❌ A pet named '{pet_name}' already exists.")
        else:
            new_pet = Pet(name=pet_name, species=species, age=int(pet_age))
            st.session_state.owner.add_pet(new_pet)
            st.success(f"✓ Added **{pet_name}** the {species}!")

# Show registered pets
pets = st.session_state.owner.get_pets()
if pets:
    with col2:
        st.markdown(f"**Registered pets:** {len(pets)}")
        for p in pets:
            st.caption(f"  • {p.get_name()} ({p.get_species()}, {p.get_age()} yrs)")
else:
    st.info("📝 Add a pet above to get started.")

if not pets:
    st.stop()

# ── Pet Selector ──────────────────────────────────────────────────

selected_pet_name = st.selectbox(
    "Select a pet to manage:",
    [p.get_name() for p in pets],
)
selected_pet = next(p for p in st.session_state.owner.pets if p.get_name() == selected_pet_name)

st.divider()

# ── Task Management ───────────────────────────────────────────────

st.subheader(f"Tasks for {selected_pet.get_name()}")

with st.expander("➕ Add a new task", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk", key="task_title_input")
    with col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20, key="duration_input")
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2, key="priority_select")

    col1, col2 = st.columns(2)
    with col1:
        category = st.text_input("Category", value="exercise", key="category_input")
    with col2:
        frequency = st.selectbox("Frequency", ["daily", "weekly", "as needed"], key="freq_select")

    if st.button("Add task", use_container_width=True):
        new_task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            category=category,
            frequency=frequency,
        )
        selected_pet.add_task(new_task)
        st.success(f"✓ Added task: **{task_title}**")

# ── Task Display & Filtering ──────────────────────────────────────

current_tasks = selected_pet.get_tasks()

if current_tasks:
    tab1, tab2, tab3 = st.tabs(["📋 All Tasks", "⏱️ By Duration", "📊 By Status"])

    with tab1:
        st.write(f"**Total tasks:** {len(current_tasks)}")
        st.table([
            {
                "Task": t.get_title(),
                "Duration (min)": t.get_duration(),
                "Priority": t.get_priority().upper(),
                "Category": t.get_category(),
                "Frequency": t.frequency,
                "Status": "✓ Done" if t.is_complete() else "⏳ Pending"
            }
            for t in current_tasks
        ])

    with tab2:
        st.write("**Sorted by duration (shortest → longest):**")
        scheduler = Scheduler(owner=st.session_state.owner, pet=selected_pet)
        sorted_tasks = scheduler.sort_by_duration(current_tasks)
        st.table([
            {
                "Duration": f"{t.get_duration()} min",
                "Task": t.get_title(),
                "Priority": t.get_priority().upper(),
                "Category": t.get_category(),
            }
            for t in sorted_tasks
        ])

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Pending tasks:**")
            scheduler = Scheduler(owner=st.session_state.owner, pet=selected_pet)
            pending = scheduler.filter_by_status(completed=False)
            if pending:
                st.table([
                    {
                        "Task": t.get_title(),
                        "Duration": f"{t.get_duration()} min",
                        "Priority": t.get_priority().upper(),
                    }
                    for t in pending
                ])
            else:
                st.success("✓ All tasks completed!")

        with col2:
            st.write("**Completed tasks:**")
            completed = scheduler.filter_by_status(completed=True)
            if completed:
                st.table([
                    {
                        "Task": t.get_title(),
                        "Frequency": t.frequency,
                    }
                    for t in completed
                ])
            else:
                st.caption("(none yet)")

else:
    st.info("📝 No tasks yet. Add one using the form above.")

st.divider()

# ── Schedule Generation ───────────────────────────────────────────

st.subheader("Generate Daily Schedule")

if st.button("🗓️ Generate schedule", use_container_width=True, type="primary"):
    if not current_tasks:
        st.error("❌ Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(owner=st.session_state.owner, pet=selected_pet)
        scheduler.generate_schedule()

        scheduled = scheduler.scheduled_tasks

        if scheduled:
            st.success(f"✓ Schedule created ({len(scheduled)} task(s), {sum(t.get_duration() for t in scheduled)} min)")

            # ── Schedule Table ────────────────────────────────────
            st.markdown("**Your Schedule:**")
            schedule_data = []
            for e in scheduler.schedule_timeline:
                task = e["task"]
                schedule_data.append({
                    "⏰ Time": f"{e['start_minute']:02d}–{e['end_minute']:02d} min",
                    "Task": task.get_title(),
                    "Duration": f"{task.get_duration()} min",
                    "Priority": f"🔴 {task.get_priority().upper()}" if task.get_priority() == "high"
                              else f"🟡 {task.get_priority().upper()}" if task.get_priority() == "medium"
                              else f"🟢 {task.get_priority().upper()}",
                    "Category": task.get_category(),
                })
            st.table(schedule_data)

            # ── Conflict Detection ─────────────────────────────────
            conflicts = scheduler.detect_conflicts()
            if conflicts:
                st.markdown("---")
                st.markdown("### ⚠️ Warnings & Conflicts")
                with st.expander("Show details", expanded=True):
                    for i, warning in enumerate(conflicts, 1):
                        if "Back-to-back" in warning:
                            st.warning(f"**Rest break needed:** {warning}")
                        elif "overlap" in warning.lower():
                            st.error(f"**Time conflict:** {warning}")
                        else:
                            st.warning(f"**⚠️ {warning}")
            else:
                st.success("✓ No conflicts detected!")

            # ── Skipped Tasks ─────────────────────────────────────
            skipped = [
                t for t in current_tasks
                if not t.is_complete() and t not in scheduled
            ]
            if skipped:
                st.markdown("---")
                st.markdown("### 📌 Tasks that didn't fit")
                with st.expander(f"Show skipped tasks ({len(skipped)})", expanded=False):
                    st.info(
                        f"These tasks don't fit in your {st.session_state.owner.available_minutes} minutes. "
                        f"Consider increasing available time or adjusting priorities."
                    )
                    skipped_data = [
                        {
                            "Task": t.get_title(),
                            "Duration": f"{t.get_duration()} min",
                            "Priority": t.get_priority().upper(),
                            "Category": t.get_category(),
                        }
                        for t in skipped
                    ]
                    st.table(skipped_data)

            # ── Schedule Explanation ───────────────────────────────
            st.markdown("---")
            with st.expander("📖 View detailed explanation"):
                st.text(scheduler.explain_schedule())

        else:
            st.error("❌ No tasks fit in the available time. Try increasing available time or removing some tasks.")

# ── Owner-Level Conflict Detection ────────────────────────────────

if len(pets) > 1:
    st.divider()
    st.subheader("🏠 Multi-Pet Scheduling")

    if st.button("Check for pet scheduling conflicts"):
        scheduler = Scheduler(owner=st.session_state.owner, pet=pets[0])
        overlaps = scheduler.detect_owner_level_overlaps()

        if overlaps:
            st.error("⚠️ **Owner-level conflicts detected!**")
            st.markdown(
                "You cannot be in two places at once. Consider:\n"
                "- Hiring a pet sitter or dog walker\n"
                "- Batching pet care into blocks\n"
                "- Adjusting task priorities or times"
            )
            with st.expander("View all conflicts"):
                for conflict in overlaps:
                    st.warning(conflict)
        else:
            st.success("✓ No scheduling conflicts between pets!")
