from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class Mode(str, Enum):
    ASSISTIVE = "ASSISTIVE"
    SEMI_AUTO = "SEMI_AUTO"
    FULL_AUTO = "FULL_AUTO"


class WebConfig(BaseModel):
    allowlist: List[str] = Field(..., min_length=1)
    require_confirm_on_submit: bool = True

    @validator("allowlist")
    def _non_empty(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("allowlist must not be empty")
        return v


class SecurityConfig(BaseModel):
    mode_default: Mode = Mode.ASSISTIVE
    web: WebConfig

    @validator("mode_default")
    def _mode_default_assistive(cls, v: Mode) -> Mode:
        if v != Mode.ASSISTIVE:
            raise ValueError("mode_default must default to ASSISTIVE")
        return v


class ModelsConfig(BaseModel):
    planner: Optional[str] = None
    judge: Optional[str] = None
    offline: str = "safe"
    vision: Optional[str] = None

    @validator("planner", "judge", "offline", "vision", pre=True, always=True)
    def _validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not isinstance(v, str) or not v.strip():
            raise ValueError("model name must be a non-empty string")
        return v
