# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PawPal+ is a Streamlit-based pet care planning assistant (AI110 Module 2 project). It helps pet owners plan daily care tasks based on constraints like time, priority, and preferences. The project involves designing the system (UML), implementing scheduling logic in Python, and connecting it to the Streamlit UI.

## Development Commands

```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the app
streamlit run app.py

# Run tests
pytest

# Run a single test file or test
pytest path/to/test_file.py
pytest path/to/test_file.py::test_function_name
```

## Architecture

- **`app.py`** — Streamlit UI entry point. Currently a starter scaffold with demo inputs (owner/pet info, task entry). The "Generate schedule" button is a placeholder that should call scheduling logic once implemented.
- **`requirements.txt`** — Dependencies: `streamlit` and `pytest`.
- **`reflection.md`** — Project reflection template to fill out after implementation.

The app uses `st.session_state.tasks` to store tasks as dicts with `title`, `duration_minutes`, and `priority` keys.

## What Needs to Be Built

The core system does not exist yet. Implementation requires:
1. Classes for tasks, pets, owners (designed from UML)
2. A scheduler that selects and orders tasks based on constraints (time available, priority, preferences)
3. Plan explanation logic (why each task was chosen/ordered)
4. Tests for key scheduling behaviors
5. Wiring the scheduler into `app.py` to replace the placeholder
