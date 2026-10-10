# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2025 Jayesh Badwaik <jayesh@ambhora.com>
# --------------------------------------------------------------------------------------------------

import pytest

import pench.base


class Enum(pench.base.ExtendedEnum):
    """Example Enum class inheriting from ExtendedEnum."""

    OPTION_ONE = "option_one"
    OPTION_TWO = "option_two"
    OPTION_THREE = "option_three"


def test_simple():
    """Test the basic functionality of the ExtendedEnum."""
    assert Enum.OPTION_ONE.value == "option_one"
    assert Enum.OPTION_TWO.value == "option_two"
    assert Enum.OPTION_THREE.value == "option_three"

    for index, option in enumerate(Enum.choices()):
        assert isinstance(option, Enum)
        assert option.value == Enum.values()[index]


def test_names_and_values_are_distinct():
    assert Enum.values() == ["option_one", "option_two", "option_three"]
    assert Enum.names() == ["OPTION_ONE", "OPTION_TWO", "OPTION_THREE"]


def test_indexes():
    assert Enum.indexes() == [0, 1, 2]


def test_from_value():
    assert Enum.from_value("option_two") is Enum.OPTION_TWO


def test_from_value_rejects_unknown():
    with pytest.raises(ValueError, match="unknown Enum 'nope'"):
        Enum.from_value("nope")
