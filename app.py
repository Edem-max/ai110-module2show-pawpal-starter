import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session-state "vault" — initialise once, survive every rerun
# ---------------------------------------------------------------------------
# st.session_state works like a dictionary that Streamlit keeps alive for the
# entire browser session. The pattern below is the standard guard:
#   "if the key doesn't exist yet → create it; otherwise → reuse what's there."
# Without this guard a fresh Owner would be created on every button click,
# wiping out all pets and tasks the user just added.

if "owner" not in st.session_state:
    st.session_state.owner = None          # set properly when owner is saved

if "pets" not in st.session_state:
    st.session_state.pets = {}             # { pet_name: Pet }

if "tasks" not in st.session_state:
    st.session_state.tasks = []            # raw dicts for the UI table

# ---------------------------------------------------------------------------
# Owner setup
# ---------------------------------------------------------------------------
st.subheader("Owner")

col_name, col_mins = st.columns(2)
with col_name:
    owner_name = st.text_input("Owner name", value="Jordan")
with col_mins:
    available_minutes = st.number_input(
        "Available minutes today", min_value=10, max_value=480, value=90
    )

if st.button("Save owner"):
    # Only create a new Owner if none exists or the name changed.
    # This is the key pattern: check before creating.
    if (
        st.session_state.owner is None
        or st.session_state.owner.name != owner_name
    ):
        st.session_state.owner = Owner(owner_name, available_minutes)
        st.session_state.pets = {}
        st.session_state.tasks = []
    else:
        # Owner already exists — just update availability in place
        st.session_state.owner.update_availability(available_minutes)
    st.success(f"Owner '{owner_name}' saved with {available_minutes} min.")

# ---------------------------------------------------------------------------
# Pet setup
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Add a Pet")

col_pet, col_species, col_age = st.columns(3)
with col_pet:
    pet_name = st.text_input("Pet name", value="Mochi")
with col_species:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col_age:
    age = st.number_input("Age", min_value=0, max_value=30, value=3)

if st.button("Add pet"):
    if st.session_state.owner is None:
        st.warning("Save an owner first.")
    elif pet_name in st.session_state.pets:
        st.info(f"{pet_name} is already added.")
    else:
        new_pet = Pet(pet_name, species, age)
        st.session_state.pets[pet_name] = new_pet
        st.session_state.owner.add_pet(new_pet)
        st.success(f"Added {pet_name} the {species}.")

if st.session_state.pets:
    st.write("Current pets:", ", ".join(st.session_state.pets.keys()))

# ---------------------------------------------------------------------------
# Task entry
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Add a Task")

PRIORITY_MAP = {"low": 1, "medium": 2, "high": 3}

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    assign_to = st.selectbox(
        "Assign to pet",
        options=list(st.session_state.pets.keys()) or ["(no pets yet)"],
    )

if st.button("Add task"):
    if st.session_state.owner is None:
        st.warning("Save an owner first.")
    elif assign_to not in st.session_state.pets:
        st.warning("Add a pet first.")
    else:
        task_id = f"t{len(st.session_state.tasks) + 1}"
        new_task = Task(
            task_id=task_id,
            name=task_title,
            category="general",
            duration_minutes=int(duration),
            priority=PRIORITY_MAP[priority],
        )
        st.session_state.pets[assign_to].add_task(new_task)
        st.session_state.tasks.append(
            {"pet": assign_to, "task": task_title, "duration_min": int(duration), "priority": priority}
        )
        st.success(f"Task '{task_title}' added to {assign_to}.")

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

# ---------------------------------------------------------------------------
# Generate schedule
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if st.session_state.owner is None or not st.session_state.pets:
        st.warning("Add an owner and at least one pet with tasks first.")
    else:
        scheduler = Scheduler(st.session_state.owner)
        plan = scheduler.generate_plan()
        st.success("Schedule generated!")
        st.text(plan.display())
