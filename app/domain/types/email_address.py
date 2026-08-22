"""Validated human account email address."""

from __future__ import annotations

from typing import Annotated

from pydantic import EmailStr, Field

type EmailAddress = Annotated[EmailStr, Field(max_length=320)]
