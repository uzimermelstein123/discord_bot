"""
One-shot script: generate .txt files from all existing JSON files in canvas_modules/.
Safe to re-run — overwrites .txt if content changed.
"""
import os
import json
from file_handler import extract_text_from_canvas_json

MODULES_FOLDER = "./canvas_modules"


def detect_type(data: dict) -> str:
    if "page_id" in data:
        return "Page"
    if "submission_types" in data or ("description" in data and "grading_type" in data):
        return "Assignment"
    if "discussion_type" in data or "message" in data:
        return "Discussion"
    return ""


def process_all():
    processed = skipped = no_content = 0

    for root, dirs, files in os.walk(MODULES_FOLDER):
        for fname in sorted(files):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                print(f"SKIP (bad JSON): {fpath}: {e}")
                skipped += 1
                continue

            item_type = detect_type(data)
            if not item_type:
                print(f"SKIP (unknown type): {fpath}")
                skipped += 1
                continue

            title = fname.replace(".json", "")
            result = extract_text_from_canvas_json(data, item_type, root, title)
            if result:
                processed += 1
            else:
                no_content += 1

    print(f"\nDone. Extracted: {processed} | No content: {no_content} | Skipped: {skipped}")


if __name__ == "__main__":
    process_all()
