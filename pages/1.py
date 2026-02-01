import streamlit as st
import json
from pathlib import Path
from collections import defaultdict

from utils.file_io import load_json
from validators.ayah_coverage import find_missing_ranges

# -----------------------------
# Paths
# -----------------------------
SURAH_CONFIG_PATH = Path("config/surah_map.json")
PARSED_DATA_DIR = Path("data/parsed")

# -----------------------------
# Load Config
# -----------------------------
surah_map = load_json(SURAH_CONFIG_PATH)

# -----------------------------
# UI
# -----------------------------
st.title("📖 Qur’an Surah Coverage (Multi-JSON)")

json_files = sorted(PARSED_DATA_DIR.glob("*.json"))

if not json_files:
    st.error("❌ No parsed JSON files found in data/parsed/")
    st.stop()

selected_files = st.multiselect(
    "Select one or more parsed JSON files",
    options=json_files,
    format_func=lambda p: p.name
)

if not selected_files:
    st.info("Select at least one JSON file to continue.")
    st.stop()

# -----------------------------
# Load & Validate Files
# -----------------------------
all_sections = []
surah_names = set()
source_files = []

for path in selected_files:
    data = load_json(path)
    surah_names.add(data["surah"])
    source_files.append(path.name)
    all_sections.extend(data.get("sections", []))

if len(surah_names) != 1:
    st.error("❌ Selected JSON files belong to different surahs.")
    st.stop()

surah_name = surah_names.pop()

if surah_name not in surah_map:
    st.error(f"❌ Surah '{surah_name}' not found in surah_map.json")
    st.stop()

surah_number = surah_map[surah_name]["surah_number"]
total_ayah = surah_map[surah_name]["total_ayah"]

# -----------------------------
# Compute Missing Ayah
# -----------------------------
missing = find_missing_ranges(all_sections, total_ayah)

# -----------------------------
# Sort & Normalize Sections
# -----------------------------
all_sections = sorted(
    all_sections,
    key=lambda s: (s["start_ayah"], s["end_ayah"])
)

# -----------------------------
# Final Integrated JSON
# -----------------------------
final_json = {
    "surah": surah_name,
    "surah_number": surah_number,
    "total_ayah": total_ayah,
    "source_files": source_files,
    "sections": all_sections,
    "missing_ayah_ranges": [
        {"start": s, "end": e} for s, e in missing
    ]
}

# -----------------------------
# Display
# -----------------------------
st.subheader("📘 Surah Metadata")
st.write(f"**Surah:** {surah_name}")
st.write(f"**Number:** {surah_number}")
st.write(f"**Total Ayah:** {total_ayah}")
st.write(f"**Source files:** {', '.join(source_files)}")

st.subheader("📑 Combined Sections")
st.json(all_sections)

st.subheader("❗ Missing Ayah Ranges")
if missing:
    for s, e in missing:
        st.write(f"• Ayah **{s}–{e}**")
else:
    st.success("No missing ayah 🎉")

st.subheader("✅ Integrated JSON")
st.json(final_json)

# -----------------------------
# Download
# -----------------------------
st.download_button(
    "⬇️ Download Combined JSON",
    data=json.dumps(final_json, indent=2, ensure_ascii=False),
    file_name=f"{surah_name.lower().replace(' ', '_')}_combined.json",
    mime="application/json"
)


# import streamlit as st
# import json
# from pathlib import Path

# from utils.file_io import load_json
# from validators.ayah_coverage import find_missing_ranges

# # -----------------------------
# # Paths
# # -----------------------------
# SURAH_CONFIG_PATH = Path("config/surah_map.json")
# PARSED_DATA_DIR = Path("data/parsed")

# # -----------------------------
# # Load Config
# # -----------------------------
# surah_map = load_json(SURAH_CONFIG_PATH)

# # -----------------------------
# # UI
# # -----------------------------
# st.title("📖 Qur’an Surah Coverage Validator")

# # ---- List available JSON files ----
# json_files = sorted(PARSED_DATA_DIR.glob("*.json"))

# if not json_files:
#     st.error("❌ No parsed JSON files found in data/parsed/")
#     st.stop()

# selected_file = st.selectbox(
#     "Select parsed Surah JSON",
#     options=json_files,
#     format_func=lambda p: p.name
# )

# # -----------------------------
# # Load Selected JSON
# # -----------------------------
# parsed_data = load_json(selected_file)

# surah_name = parsed_data["surah"]

# if surah_name not in surah_map:
#     st.error(f"❌ Surah '{surah_name}' not found in surah_map.json")
#     st.stop()

# surah_number = surah_map[surah_name]["surah_number"]
# total_ayah = surah_map[surah_name]["total_ayah"]

# sections = parsed_data.get("sections", [])

# # -----------------------------
# # Compute Missing Ayah
# # -----------------------------
# missing = find_missing_ranges(sections, total_ayah)

# # -----------------------------
# # Merge & Enrich JSON
# # -----------------------------
# final_json = {
#     "surah": surah_name,
#     "surah_number": surah_number,
#     "total_ayah": total_ayah,
#     "source_file": selected_file.name,
#     "sections": sections,
#     "missing_ayah_ranges": [
#         {"start": s, "end": e} for s, e in missing
#     ]
# }

# # -----------------------------
# # Display
# # -----------------------------
# st.subheader("📘 Surah Metadata")
# st.write(f"**Surah:** {surah_name}")
# st.write(f"**Number:** {surah_number}")
# st.write(f"**Total Ayah:** {total_ayah}")

# st.subheader("📑 Parsed Sections")
# st.json(sections)

# st.subheader("❗ Missing Ayah Ranges")
# if missing:
#     for s, e in missing:
#         st.write(f"• Ayah **{s}–{e}**")
# else:
#     st.success("No missing ayah 🎉")

# st.subheader("✅ Final Integrated JSON")
# st.json(final_json)

# # -----------------------------
# # Download
# # -----------------------------
# st.download_button(
#     "⬇️ Download Enriched JSON",
#     data=json.dumps(final_json, indent=2, ensure_ascii=False),
#     file_name=f"{surah_name.lower().replace(' ', '_')}_validated.json",
#     mime="application/json"
# )
