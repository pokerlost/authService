"""Direct ORM entity response configuration."""

from __future__ import annotations

from pydantic import ConfigDict

from .response_model import ResponseModel


class ORMSchema(ResponseModel):
    """Public schema serialized from explicit ORM attributes."""

    model_config = ConfigDict(from_attributes=True)
