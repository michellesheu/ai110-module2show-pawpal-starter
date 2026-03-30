import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner Info")
owner_name = st.text_input("Owner name", value="Jordan")
available_time = st.number_input("Available time (minutes)", min_value=1, max_value=480, value=30)

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=30, pets=[])

if st.button("Save owner info"):
    st.session_state.owner.name = owner_name
    st.session_state.owner.available_minutes = int(available_time)
    st.success(f"Owner info saved for {owner_name}.")

st.divider()

st.subheader("Add a Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
pet_age = st.number_input("Pet age (years)", min_value=0, max_value=30, value=3)

if st.button("Add pet"):
    # Prevent duplicate pet names
    existing_names = [p.get_name().lower() for p in st.session_state.owner.get_pets()]
    if pet_name.lower() in existing_names:
        st.warning(f"A pet named '{pet_name}' already exists.")
    else:
        new_pet = Pet(name=pet_name, species=species, age=int(pet_age))
        st.session_state.owner.add_pet(new_pet)
        st.success(f"Added {pet_name} the {species}!")

# Show current pets and select one
pets = st.session_state.owner.get_pets()
if pets:
    st.markdown(f"**Registered pets ({len(pets)}):** " + ", ".join(p.get_name() for p in pets))
    selected_pet_name = st.selectbox(
        "Select a pet to manage",
        [p.get_name() for p in pets],
    )
    # get_pets() returns copies, so look up the actual Pet object in owner.pets
    selected_pet = next(p for p in st.session_state.owner.pets if p.get_name() == selected_pet_name)
else:
    selected_pet = None
    st.info("Add a pet above to get started.")

if selected_pet is not None:
    st.markdown(f"### Tasks for {selected_pet.get_name()}")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col4:
        category = st.text_input("Category", value="exercise")
    with col5:
        frequency = st.selectbox("Frequency", ["daily", "weekly", "as needed"])

    if st.button("Add task"):
        new_task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            category=category,
            frequency=frequency,
        )
        selected_pet.add_task(new_task)

    current_tasks = selected_pet.get_tasks()
    if current_tasks:
        st.write("Current tasks:")
        st.table([
            {"title": t.get_title(), "duration_minutes": t.get_duration(),
             "priority": t.get_priority(), "category": t.get_category()}
            for t in current_tasks
        ])
    else:
        st.info("No tasks yet. Add one above.")

    st.divider()

    st.subheader("Build Schedule")

    if st.button("Generate schedule"):
        if not selected_pet.get_tasks():
            st.warning("Add at least one task before generating a schedule.")
        else:
            scheduler = Scheduler(owner=st.session_state.owner, pet=selected_pet)
            scheduler.generate_schedule()

            scheduled = scheduler.scheduled_tasks
            if scheduled:
                st.success(f"Scheduled {len(scheduled)} task(s)")
                st.table([
                    {
                        "start (min)": e["start_minute"],
                        "end (min)": e["end_minute"],
                        "task": e["task"].get_title(),
                        "priority": e["task"].get_priority(),
                        "category": e["task"].get_category(),
                        "frequency": e["task"].frequency,
                        "duration": e["task"].get_duration(),
                    }
                    for e in scheduler.schedule_timeline
                ])

                conflicts = scheduler.detect_conflicts()
                for w in conflicts:
                    st.warning(w)

                skipped = [
                    t for t in selected_pet.get_tasks()
                    if not t.is_complete() and t not in scheduled
                ]
                if skipped:
                    st.info("Skipped (not enough time): " + ", ".join(t.get_title() for t in skipped))
            else:
                st.warning("No tasks fit in the available time.")
