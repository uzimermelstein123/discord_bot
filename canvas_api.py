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
        print(f"Endpoint {CANVAS_API_URL}{endpoint}")
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