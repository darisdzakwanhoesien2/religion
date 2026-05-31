import json
from datetime import datetime

import streamlit as st

from utils.file_io import load_json, save_json
from parsers.surah_summary_parser import parse_sections
from validators.ayah_coverage import find_missing_ranges

# -----------------------------
# Load Surah Metadata
# -----------------------------
SURAH_MAP = load_json("config/surah_map.json")

# -----------------------------
# UI
# -----------------------------
st.title("📖 Qur’an Surah Summary Parser")

surah_name = st.selectbox(
    "Select Surah",
    options=list(SURAH_MAP.keys())
)

surah_number = SURAH_MAP[surah_name]["surah_number"]
total_ayah = SURAH_MAP[surah_name]["total_ayah"]

st.info(
    f"**Surah:** {surah_name}\n\n"
    f"**Number:** {surah_number}\n\n"
    f"**Total Ayah:** {total_ayah}"
)

raw_text = st.text_area(
    "Paste bullet-style summary here",
    height=350,
    placeholder="* **Verses 1–5 (The Righteous):** The Surah begins..."
)

if raw_text.strip():
    sections = parse_sections(raw_text)

    if not sections:
        st.error("❌ No valid sections detected. Check formatting.")
    else:
        # Compute coverage gaps so users can quickly see missing ayah ranges.
        missing = find_missing_ranges(sections, total_ayah)

        result = {
            "surah": surah_name,
            "surah_number": surah_number,
            "total_ayah": total_ayah,
            "sections": sections,
            "missing_ayah_ranges": [
                {"start": s, "end": e} for s, e in missing
            ],
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }

        st.subheader("✅ Parsed JSON")
        st.json(result)

        st.subheader("❗ Missing Ayah Ranges")
        if missing:
            for s, e in missing:
                st.write(f"• Ayah **{s}–{e}**")
        else:
            st.success("No missing ayah 🎉")

        # Save automatically
        filename = f"data/parsed/{surah_name.lower().replace(' ', '_')}.json"
        save_json(result, filename)

        st.success(f"Saved to `{filename}`")

        st.download_button(
            "⬇️ Download JSON",
            data=json.dumps(result, indent=2),
            file_name=f"{surah_name.lower().replace(' ', '_')}.json",
            mime="application/json"
        )
