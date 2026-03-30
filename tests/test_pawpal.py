"""Tests for PawPal+ core logic."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet


def test_mark_complete_changes_status():
    task = Task(title="Morning Walk", duration_minutes=30, priority="high", category="exercise")
    assert task.is_complete() is False
    task.mark_complete()
    assert task.is_complete() is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", species="Dog", age=3)
    assert len(pet.get_tasks()) == 0
    task = Task(title="Feeding", duration_minutes=10, priority="high", category="nutrition")
    pet.add_task(task)
    assert len(pet.get_tasks()) == 1
