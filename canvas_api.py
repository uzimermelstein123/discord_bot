import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()
CANVAS_API_KEY = os.getenv("CANVAS_API_KEY")
CANVAS_API_URL = os.getenv("CANVAS_API_URL")

def make_canvas_request(endpoint: str, params: dict = None):
    """
    Makes an authenticated GET request to the Canvas API.
    :param endpoint: The API endpoint (e.g., "/courses").
    :param params: Optional query parameters for the request.
    :return: The JSON response from the API.
    """
    try:
        print(f"Request for endpoint : {CANVAS_API_URL}{endpoint}")
        response = requests.get(
            f"{CANVAS_API_URL}{endpoint}",
            headers={
                "Authorization": f"Bearer {CANVAS_API_KEY}",
                "Accept": "application/json",
            },
            params=params,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request to Canvas API: {e}")
        return None

def get_courses():
    """
    Retrieves a list of courses for the authenticated user.
    """
    print("Fetching courses...")
    params = {"enrollment_state": "active"}
    courses = make_canvas_request("/api/v1/courses", params=params)
    
    if courses:
        print("Courses retrieved successfully.")
        pretty_json_output = json.dumps(courses, indent=4)
        print(pretty_json_output)
    else:
        print("Failed to retrieve courses.")
    
    return courses

def get_course_attributes(course_id: int):
    """
    Retrieves assignments for a specific course.
    :param course_id: The ID of the course to retrieve assignments for.
    :return: List of assignments
    """
    print(f"Fetching attributes for course ID {course_id}...\n")
    assignments = make_canvas_request(f"/api/v1/courses/{course_id}/assignments")
    
    if assignments:
        print(f"Retrieved {len(assignments)} assignments.")
    else:
        print(f"Failed to retrieve assignments for course {course_id}.")
    
    return assignments or []

def get_module_html_urls(course_id: int, course_name: str = ""):
    """
    Retrieves all html_urls for items across all modules in a course.
    :param course_id: The ID of the course.
    :param course_name: Optional course name for display purposes.
    :return: List of dicts with module/item info and html_urls.
    """
    modules = make_canvas_request(f"/api/v1/courses/{course_id}/modules")

    if not modules:
        print(f"No modules found for course: {course_name or course_id}")
        return []

    results = []
    print(f"\nCourse: {course_name or course_id}")
    print("=" * 50)

    for module in modules:
        print(f"\n  Module: {module['name']} (ID: {module['id']})")
        print(f"  {'-' * 40}")

        if not module.get("items_url"):
            print("    No items URL for this module.")
            continue

        items_url = module["items_url"].replace(CANVAS_API_URL, "")
        items = make_canvas_request(items_url)

        if not items:
            print("    No items found.")
            continue

        for item in items:
            html_url = item.get("html_url")
            title = item.get("title", "Untitled")
            item_type = item.get("type", "Unknown")
            print(f"    [{item_type}] {title}")
            print(f"      URL: {html_url}")
            results.append({"module": module["name"], "title": title, "type": item_type, "html_url": html_url})

    return results


if __name__ == "__main__":
    params = {"enrollment_state": "active"}
    courses = make_canvas_request("/api/v1/courses", params=params)

    for course in courses:
        if course["enrollment_term_id"] == 1:
            continue
        # urls = get_module_html_urls(course["id"], course["name"])
        # print(urls)
        get_module_html_urls(course["id"], course["name"])
        
