"""
Intermediate and final results that we get from LLMs.
"""

from dataclasses import dataclass
from enum import StrEnum


@dataclass
class Metadata:
    service_name: str
    service_nature: str
    document_type: str
    document_language: str


class Score(StrEnum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"


@dataclass
class Summary:
    score: Score
    summary: str
