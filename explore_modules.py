"""
Exploratory script to print all modules and item types for each course.
Run this to see what's in your Canvas modules before deciding how to handle them.
"""
from canvas_api import get_courses, make_canvas_request
import os

def explore_modules():
    courses = get_courses()

    if not courses:
        print("No courses found.")
        return

    for course in courses:
        if course.get("enrollment_term_id") == 1:
            continue

        course_id = course["id"]
        course_name = course.get("name", "Unknown")
        print(f"\n{'='*60}")
        print(f"COURSE: {course_name} (ID: {course_id})")
        print(f"{'='*60}")

        modules = make_canvas_request(f"/api/v1/courses/{course_id}/modules")
        if not modules:
            print("  No modules found.")
            continue

        for module in modules:
            print(f"\n  MODULE: {module['name']} (ID: {module['id']})")
            print(f"  {'-'*50}")

            items_url = module.get("items_url", "")
            if not items_url:
                print("    (no items)")
                continue

            base_url = os.getenv("CANVAS_API_URL", "")
            items_endpoint = items_url.replace(base_url, "")
            items = make_canvas_request(items_endpoint)

            if not items:
                print("    (no items)")
                continue

            for item in items:
                item_type = item.get("type", "Unknown")
                title = item.get("title", "Untitled")
                content_id = item.get("content_id")
                page_url = item.get("page_url")
                url = item.get("url")
                html_url = item.get("html_url")

                print(f"    [{item_type}] {title}")
                if content_id:
                    print(f"      content_id : {content_id}")
                if page_url:
                    print(f"      page_url   : {page_url}")
                if url:
                    print(f"      api_url    : {url}")
                if html_url:
                    print(f"      html_url   : {html_url}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    explore_modules()
