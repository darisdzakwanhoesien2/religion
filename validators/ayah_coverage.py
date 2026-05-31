from __future__ import annotations

from typing import Iterable


def _normalize_covered_ranges(sections: Iterable[dict], total_ayah: int) -> list[tuple[int, int]]:
    """
    Convert section dicts into normalized, clamped (start, end) ranges.

    Normalization rules:
    - If a section has start/end reversed, swap them.
    - Clamp ranges to [1, total_ayah].
    - Drop ranges that don't overlap [1, total_ayah] after clamping.
    """
    if total_ayah < 1:
        return []

    covered: list[tuple[int, int]] = []
    for section in sections:
        try:
            start = int(section["start_ayah"])
            end = int(section["end_ayah"])
        except Exception:
            # Skip malformed entries rather than crashing the UI.
            continue

        if start > end:
            start, end = end, start

        start = max(1, start)
        end = min(total_ayah, end)
        if start > end:
            continue

        covered.append((start, end))

    covered.sort(key=lambda r: (r[0], r[1]))
    return covered


def find_missing_ranges(sections: Iterable[dict], total_ayah: int) -> list[tuple[int, int]]:
    """
    Return a list of (start, end) ayah ranges not covered by the provided sections.

    Sections are treated as inclusive ranges. Overlaps are merged implicitly during the scan.
    """
    covered = _normalize_covered_ranges(sections, total_ayah)

    if total_ayah < 1:
        return []

    if not covered:
        return [(1, total_ayah)]

    missing: list[tuple[int, int]] = []
    current = 1

    for start, end in covered:
        if start > current:
            missing.append((current, start - 1))
        current = max(current, end + 1)

        if current > total_ayah:
            break

    if current <= total_ayah:
        missing.append((current, total_ayah))

    return missing


# def find_missing_ranges(sections, total_ayah):
#     if not sections:
#         return [(1, total_ayah)]

#     covered = sorted(
#         [(s["start_ayah"], s["end_ayah"]) for s in sections],
#         key=lambda x: x[0]
#     )

#     missing = []
#     current = 1

#     for start, end in covered:
#         if start > current:
#             missing.append((current, start - 1))
#         current = max(current, end + 1)

#     if current <= total_ayah:
#         missing.append((current, total_ayah))

#     return missing
