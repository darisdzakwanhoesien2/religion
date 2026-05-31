import re

SECTION_PATTERN = re.compile(
    r"Verses\s+(\d+)\s*[–-]\s*(\d+)\s*\((.*?)\):\*\*\s*(.*)",
    re.IGNORECASE
)

def parse_sections(raw_text: str) -> list[dict]:
    """
    Parse bullet-style Markdown lines into section dicts.

    Expected format per line (commonly produced by LLM prompts):
      * **Verses 1–5 (Theme):** Summary...

    Lines that don't match are ignored.
    """
    sections: list[dict] = []

    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue

        # Remove bullets / leading Markdown so the regex can match consistently.
        line = line.lstrip("* ").strip()

        match = SECTION_PATTERN.search(line)
        if not match:
            continue

        start, end, theme, summary = match.groups()

        start_ayah = int(start)
        end_ayah = int(end)
        if start_ayah > end_ayah:
            # Be forgiving: occasionally ranges are accidentally reversed.
            start_ayah, end_ayah = end_ayah, start_ayah

        sections.append(
            {
                "start_ayah": start_ayah,
                "end_ayah": end_ayah,
                "theme": theme.strip(),
                "summary": summary.strip(),
            }
        )

    return sections
