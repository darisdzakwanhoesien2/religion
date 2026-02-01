def find_missing_ranges(sections, total_ayah):
    if not sections:
        return [(1, total_ayah)]

    covered = sorted(
        [(s["start_ayah"], s["end_ayah"]) for s in sections],
        key=lambda x: x[0]
    )

    missing = []
    current = 1

    for start, end in covered:
        if start > current:
            missing.append((current, start - 1))
        current = max(current, end + 1)

    if current <= total_ayah:
        missing.append((current, total_ayah))

    return missing
