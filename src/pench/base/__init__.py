# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2025 Jayesh Badwaik <jayesh@ambhora.com>
# --------------------------------------------------------------------------------------------------

"""Small shared primitives used across pench."""

import enum
import typing


class ExtendedEnum(enum.Enum):
    """Extended Enum to support additional convenience methods."""

    @classmethod
    def choices(cls) -> typing.List["ExtendedEnum"]:
        """Return a list of all enum members."""
        return list(cls)

    @classmethod
    def values(cls) -> typing.List[str]:
        """Return a list of all enum member values."""
        return [member.value for member in cls]

    @classmethod
    def names(cls) -> typing.List[str]:
        """Return a list of all enum member names."""
        return [member.name for member in cls]

    @classmethod
    def indexes(cls) -> typing.List[int]:
        """Return the zero-based positional index of every enum member."""
        return [index for index, _ in enumerate(cls)]

    @classmethod
    def from_value(cls, value: str) -> "ExtendedEnum":
        """
        Look a member up by its value, raising a helpful error when it is unknown.

        :param value: The value to look up.
        :raises ValueError: If no member carries that value.
        """
        try:
            return cls(value)
        except ValueError:
            allowed = ", ".join(cls.values())
            raise ValueError(f"unknown {cls.__name__} '{value}' (expected one of: {allowed})")
