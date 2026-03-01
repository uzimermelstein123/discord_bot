import requests
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import pdfplumber
import mimetypes
from docx import Document
import json
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
    # print(courses)
    pretty_json_output = json.dumps(courses, indent=4)
    print(pretty_json_output)
    if courses:
        print("Courses retrieved successfully.")
        # Example: Print course attributes
        # for course in courses:
        # print(courses)
        # for course in courses:
        #     course_name = course_name = course.get('name', 'Name Hidden (Restricted)')
        #     print(course_name)
        course_id = courses[6].get('id')
        course_name = courses[6].get('name', 'Name Hidden (Restricted)')
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
    """
    Parses assignment description to extract file IDs and downloads files.
    If no files with data-api-endpoint are found, returns the HTML description.
    :param assignment: The assignment object from Canvas API
    :return: Dictionary of extracted files or HTML data if no files found
    """
    html_data = assignment.get('description', '')
    
    # Handle case where description is None or empty
    if not html_data:
        print("No description found in assignment.")
        return {}
    
    soup = BeautifulSoup(html_data, 'html.parser')
    extracted_files = {}
    
    # Find all links that have the data-api-endpoint attribute
    links_with_endpoint = soup.find_all('a', attrs={'data-api-endpoint': True})
    
    # If links with data-api-endpoint exist, download them
    if links_with_endpoint:
        for link in links_with_endpoint:
            endpoint = link['data-api-endpoint']
            title = link.get('title', link.get('Title', 'No Title'))
            
            print(f"File Title: {title}")
            
            # Extract file ID from endpoint
            file_id = endpoint.split('/')[-1]
            
            download_to_server(file_id)
            print(f"Downloaded File ID: {file_id}\n")
            
            extracted_files[file_id] = title
    else:
        # No files with data-api-endpoint found, return HTML data
        print("No files with data-api-endpoint found in assignment description.")
        print(f"Assignment Description (HTML):\n{html_data}\n")
        extracted_files['html_content'] = html_data
    
    return html_data

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
    print(f"File text: \n")
    check_file(save_path)
    return save_path

# def check_file(file_path, output_folder="./ai_context"):
#     """
#     Checks if the file is a valid PDF and extracts text from its pages.
#     :param file_path: The path to the file to check.
#     """
#     # Check if the file has a .pdf extension
#     if not file_path.lower().endswith('.pdf'):
#         print(f"Error: The file '{file_path}' is not a PDF.")
#         return

#     # Check if the file's MIME type is application/pdf
#     mime_type, _ = mimetypes.guess_type(file_path)
#     if mime_type != 'application/pdf':
#         print(f"Error: The file '{file_path}' is not a valid PDF (MIME type: {mime_type}).")
#         return

#     # Open the file with pdfplumber and iterate through its pages
#     try:
#         with pdfplumber.open(file_path) as pdf:
#             if not pdf.pages:
#                 print(f"Error: The file '{file_path}' has no pages.")
#                 return

#             print(f"Extracting text from the file '{file_path}'...")
#             pages_text = []
#             for i, page in enumerate(pdf.pages):
#                 print(f"Page {i + 1}:")
#                 page_text = page.extract_text()
#                 print(page_text)   # Extract and print text from the page
#                 pages_text.append(page_text)
#                 print("-" * 40)
                
#             output_file = os.path.join(output_folder, os.path.basename(file_path).replace('.pdf', '.txt'))
#             with open(output_file, 'w', encoding='utf-8') as f:
#                 # for page_text in pages_text:
#                 f.write("\n".join(pages_text))
#             print(f"Extracted text saved to: {output_file}")
#     except Exception as e:
#         print(f"Error processing the file '{file_path}': {e}")

def check_file(file_path, output_folder="./ai_context"):
    """
    Checks if the file is a valid PDF or DOCX and extracts text from its pages/paragraphs.
    Saves the extracted text to the ai_context folder.
    :param file_path: The path to the file to check.
    :param output_folder: The folder where extracted text will be saved.
    """
    # Ensure the directory exists
    os.makedirs(output_folder, exist_ok=True)

    file_extension = file_path.lower().split('.')[-1]

    # Handle PDF files
    if file_extension == 'pdf':
        # Check if the file's MIME type is application/pdf
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type != 'application/pdf':
            print(f"Error: The file '{file_path}' is not a valid PDF (MIME type: {mime_type}).")
            return

        # Open the file with pdfplumber and iterate through its pages
        try:
            with pdfplumber.open(file_path) as pdf:
                if not pdf.pages:
                    print(f"Error: The file '{file_path}' has no pages.")
                    return

                print(f"Extracting text from PDF '{file_path}'...")
                pages_text = []
                for i, page in enumerate(pdf.pages):
                    print(f"Page {i + 1}:")
                    page_text = page.extract_text()
                    print(page_text)  # Extract and print text from the page
                    pages_text.append(f"Page {i + 1}:\n{page_text}")
                    print("-" * 40)

                # Save extracted text to file
                output_file = os.path.join(output_folder, os.path.basename(file_path).replace('.pdf', '.txt'))
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("\n".join(pages_text))
                print(f"Extracted text saved to: {output_file}\n")
        except Exception as e:
            print(f"Error processing PDF file '{file_path}': {e}\n")

    # Handle DOCX files
    elif file_extension == 'docx':
        # Check if the file's MIME type is correct for DOCX
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type != 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            print(f"Warning: The file '{file_path}' may not be a valid DOCX (MIME type: {mime_type}).")

        # Open the DOCX file and extract text
        try:
            doc = Document(file_path)
            print(f"Extracting text from DOCX '{file_path}'...")
            extracted_text = ""
            
            for i, paragraph in enumerate(doc.paragraphs):
                print(f"Paragraph {i + 1}: {paragraph.text}")
                extracted_text += paragraph.text + "\n"

            # Save extracted text to file
            output_file = os.path.join(output_folder, os.path.basename(file_path).replace('.docx', '.txt'))
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(extracted_text)
            print(f"Extracted text saved to: {output_file}\n")
        except Exception as e:
            print(f"Error processing DOCX file '{file_path}': {e}\n")

    # Unsupported file type
    else:
        print(f"Error: The file '{file_path}' is not a supported file type (PDF or DOCX).\n")
# Example usage
if __name__ == "__main__":
    # Fetch all courses
    get_courses()

    # Fetch attributes for a specific course (replace with a valid course ID)
    # course_id = 191199  # Replace with an actual course ID
    # get_course_attributes(course_id)