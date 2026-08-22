"""Secret-aware bounded plaintext password input."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field, SecretStr

type PasswordValue = Annotated[SecretStr, Field(min_length=12, max_length=1024)]
