"""
Pipeline for estimating how long an assignment will take.
Reads stored context from assignments/ and queries Azure AI.
"""
import os
from azure_ai import get_assignment_time_estimate

ASSIGNMENTS_FOLDER = "./assignments"
MAX_CONTEXT_CHARS = 6000


def _collect_text_from_folder(folder_path: str) -> str:
    """Read all .txt and .html files in a folder and return combined text."""
    parts = []
    for fname in sorted(os.listdir(folder_path)):
        if fname.endswith((".txt", ".html")):
            fpath = os.path.join(folder_path, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().strip()
                if content:
                    parts.append(f"--- {fname} ---\n{content}")
            except OSError:
                pass
    return "\n\n".join(parts)


def find_assignment(query: str) -> tuple[str | None, str | None, str | None]:
    """
    Search assignments/ for a folder matching the query (case-insensitive substring).
    Returns (course_name, assignment_name, folder_path) or (None, None, None).
    """
    query_lower = query.lower()
    if not os.path.isdir(ASSIGNMENTS_FOLDER):
        return None, None, None

    for course_name in os.listdir(ASSIGNMENTS_FOLDER):
        course_path = os.path.join(ASSIGNMENTS_FOLDER, course_name)
        if not os.path.isdir(course_path):
            continue
        for assignment_name in os.listdir(course_path):
            if query_lower in assignment_name.lower():
                assignment_path = os.path.join(course_path, assignment_name)
                if os.path.isdir(assignment_path):
                    return course_name, assignment_name, assignment_path

    return None, None, None


def estimate_assignment_time(assignment_query: str) -> str:
    """
    Given a user's assignment name query, find the stored context and
    return an AI-generated time estimate.
    """
    course_name, assignment_name, folder_path = find_assignment(assignment_query)

    if not folder_path:
        return (
            f"I couldn't find an assignment matching \"{assignment_query}\" in my stored data. "
            "Try running the assignments pipeline first, or check the assignment name."
        )

    context = _collect_text_from_folder(folder_path)

    if not context:
        return (
            f"Found assignment **{assignment_name}** ({course_name}) but no readable content is stored yet. "
            "Run the assignments pipeline to download and extract the assignment files first."
        )

    # Truncate to keep within token limits
    if len(context) > MAX_CONTEXT_CHARS:
        context = context[:MAX_CONTEXT_CHARS] + "\n\n[...content truncated...]"

    return get_assignment_time_estimate(
        assignment_name=assignment_name,
        course_name=course_name,
        context=context,
    )

