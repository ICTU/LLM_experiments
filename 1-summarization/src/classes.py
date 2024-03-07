from __future__ import annotations
from typing import TypedDict


class Summary(TypedDict):
    """A summary of a code file, component, application, or complete system."""

    path: str
    summary: str
    summaries: list[Summary]
    details: Configurations
    

class Configurations(TypedDict):
    """Models and application configurations"""

    time: str
    max_base_tokens_code: int
    max_base_tokens_summaries: int
    model_type: str
    model_name: str
    prompts: dict