import requests
from dotenv import load_dotenv
import os

load_dotenv()
CANVAS_API_KEY = os.getenv("CANVAS_API_KEY")
CANVAS_API_URL = os.getenv("CANVAS_API_URL")  # Add this to your .env file (e.g., https://your-canvas-instance.instructure.com/api/v1)

# Function to make authenticated requests to the Canvas API
def make_canvas_request(endpoint: str, params: dict = None):
    """
    Makes an authenticated GET request to the Canvas API.
    :param endpoint: The API endpoint (e.g., "/courses").
    :param params: Optional query parameters for the request.
    :return: The JSON response from the API.
    """
    try:
        response = requests.get(
            f"{CANVAS_API_URL}{endpoint}?enrollment_state=active", #enrollment state=active is great from gemini
            headers={
                "Authorization": f"Bearer {CANVAS_API_KEY}",  # Use Bearer token for authentication
                "Accept": "application/json",
            },
            params=params,
        )
        response.raise_for_status()  # Raise an error for HTTP status codes 4xx/5xx
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request to Canvas API: {e}")
        return None

# Get all courses
def get_courses():
    """
    Retrieves a list of courses for the authenticated user.
    """
    print("Fetching courses...")
    courses = make_canvas_request("/courses")
    if courses:
        print("Courses retrieved successfully.")
        # Example: Print course attributes
        # for course in courses:
        course_id = courses[1].get('id')
        course_name = courses[1].get('name', 'Name Hidden (Restricted)')
        # print(course)
        print(course_id, " | " ,course_name)
        get_course_attributes(course_id)
            # break
            # break
            # print(f"Course ID: {course['id']}, Name: {course['name']}")
    else:
        print("Failed to retrieve courses.")

# Get class attributes for a specific course
def get_course_attributes(course_id: int):
    """
    Retrieves attributes for a specific course.
    :param course_id: The ID of the course to retrieve attributes for.
    """

    print(f"Fetching attributes for course ID {course_id}...\n")
    course = make_canvas_request(f"/courses/{course_id}") # Can remove /assignments need to see differences, also can add assignment id if necessary
    assignments = make_canvas_request(f"/courses/{course_id}/assignments") # Can remove /assignments need to see differences, also can add assignment id if necessary
    
    for i, assignment in enumerate(assignments):
        print(f"Assignment {i} in assignments{assignment}\n")
        if 'attachments in assignment':
            print(f"There are attachments {assignment["attachements"]}\n")
        
    return
        # assignment_details = make_canvas_request(f"/courses/{course_id}/assignments/{assignment}")
    # print("Course is ", course)
    
    
    # print("Course ID {}")
    print("Assignments are \n", assignments[0])
    print(f"Assignment (ID 2593917 )details \n {assignment_details}")
    print("Assignments and details are equal", assignments[0] == assignment_details)
    print("---------------------\n")
    # if course:
    #     print("Course attributes retrieved successfully.")
    #     # Example: Print course attributes
    #     print(course)
        
    #     # print(f"Course Name: {course['name']}")
    #     # print(f"Course Code: {course['course_code']}")
    #     # print(f"Start Date: {course['start_at']}")
    #     # print(f"End Date: {course['end_at']}")
    # else:
    #     print(f"Failed to retrieve attributes for course ID {course_id}.")
    
# Example usage
if __name__ == "__main__":
    # Fetch all courses
    get_courses()

    # Fetch attributes for a specific course (replace with a valid course ID)
    # course_id = 191199  # Replace with an actual course ID
    # get_course_attributes(course_id)