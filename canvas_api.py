import requests
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup

# from parse_description import parse_assignment_description_for_fileid


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
        print(f"Endpoint {CANVAS_API_URL}{endpoint}")
        response = requests.get(
            f"{CANVAS_API_URL}{endpoint}", #?enrollment_state=active", #enrollment state=active is great from gemini
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
    # courses = make_canvas_request("/api/v1/courses")
    params = {"enrollment_state": "active"}  # Add this to filter for active courses
    courses = make_canvas_request("/api/v1/courses", params=params)
    
    if courses:
        print("Courses retrieved successfully.")
        # Example: Print course attributes
        # for course in courses:
        # print(courses)
        # for course in courses:
        #     course_name = course_name = course.get('name', 'Name Hidden (Restricted)')
        #     print(course_name)
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
    # course = make_canvas_request(f"/api/v1/courses/{course_id}") # Can remove /assignments need to see differences, also can add assignment id if necessary
    assignments = make_canvas_request(f"/api/v1/courses/{course_id}/assignments") # Can remove /assignments need to see differences, also can add assignment id if necessary
    print(assignments)
    for i, assignment in enumerate(assignments):
        print(f"Assignment {i} in assignments{assignment}\n")
        
        parse_assignment_description_for_fileid(assignment)
        
    # file_map = parse_assignment_description_for_fileid(assignment)

    # for fid, title in file_map.items():
    #     print(f"Syncing {title}...")
    #     local_path = download_to_server(fid)

def parse_assignment_description_for_fileid(assignment):
    html_data = assignment['description'] 
    soup = BeautifulSoup(html_data, 'html.parser')

    extracted_files = {}
    # Find all links that have the data-api-endpoint attribute
    for link in soup.find_all('a', attrs={'data-api-endpoint': True}):
        endpoint = link['data-api-endpoint']
        title = link.get('title', link.get('Title', 'No Title'))
        
        print(f"File Title: {title}")
        # print(f"API Endpoint: {endpoint}")
        
        # To get just the ID, split the string
        file_id = endpoint.split('/')[-1]
        
        download_to_server(file_id)
        print(f"Downlaoded File ID: {file_id}\n")
        
        # extracted_files[file_id] = title
        
        # download_canvas_file(file_id)
        
    # Print extracted_files only once at the end
    # print(extracted_files)
    
    return extracted_files

def download_to_server(file_id, output_folder="./ai_context"):
    # 1. Get the file metadata to find the actual download URL
    # Canvas often redirects to an AWS S3 bucket
    file_info = make_canvas_request(f"/files/{file_id}")
    print(f"File info: {file_info}")
    
    if not file_info or 'url' not in file_info["attachment"]:
        print(f"Error: Could not get download URL for {file_id}")
        return None
    file_attachment = file_info['attachment']
    download_url = file_attachment['url']
    filename = file_attachment.get('display_name', f"temp_{file_id}.pdf")
    save_path = os.path.join(output_folder, filename)

    # Ensure the directory exists
    os.makedirs(output_folder, exist_ok=True)

    # 2. Perform the actual download to YOUR end
    # Use stream=True to handle large files without crashing memory
    print(f"Routing download for {filename} to local end...")
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    
    print(f"File stored at: {save_path}")
    return save_path

# Example usage
if __name__ == "__main__":
    # Fetch all courses
    get_courses()

    # Fetch attributes for a specific course (replace with a valid course ID)
    # course_id = 191199  # Replace with an actual course ID
    # get_course_attributes(course_id)