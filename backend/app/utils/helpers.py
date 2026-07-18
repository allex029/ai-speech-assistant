"""Miscellaneous helpers."""

import re
from typing import Iterable


def tokenize_words(text: str) -> list[str]:
    """Split transcript into lowercase word tokens."""
    if not text:
        return []
    return re.findall(r"[a-zA-Z']+", text.lower())


def count_words(text: str) -> int:
    return len(tokenize_words(text))


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def unique_preserve_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
