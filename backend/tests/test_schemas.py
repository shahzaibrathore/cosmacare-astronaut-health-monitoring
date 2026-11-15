"""Tests for Pydantic validation schemas."""

import pytest
from pydantic import ValidationError

from app.schemas import CrewCreate


def test_crew_create_accepts_valid_name():
    crew = CrewCreate(name="Shahzaib")
    assert crew.name == "Shahzaib"


def test_crew_create_trims_extra_spaces():
    crew = CrewCreate(name=" Shahzaib ")
    assert crew.name == "Shahzaib"


def test_crew_create_rejects_empty_name():
    with pytest.raises(ValidationError):
        CrewCreate(name="")


def test_crew_create_rejects_whitespace_only_name():
    with pytest.raises(ValidationError):
        CrewCreate(name="   ")


def test_crew_create_rejects_name_over_100_characters():
    with pytest.raises(ValidationError):
        CrewCreate(name="A" * 101)
