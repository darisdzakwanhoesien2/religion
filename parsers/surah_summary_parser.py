import re

SECTION_PATTERN = re.compile(
    r"Verses\s+(\d+)\s*[–-]\s*(\d+)\s*\((.*?)\):\*\*\s*(.*)",
    re.IGNORECASE
)

def parse_sections(raw_text: str):
    sections = []

    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue

        # remove bullets and leading markdown
        line = line.lstrip("* ").strip()

        match = SECTION_PATTERN.search(line)
        if not match:
            continue

        start, end, theme, summary = match.groups()

        sections.append({
            "start_ayah": int(start),
            "end_ayah": int(end),
            "theme": theme.strip(),
            "summary": summary.strip()
        })

    return sections
