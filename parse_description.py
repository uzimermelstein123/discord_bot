from bs4 import BeautifulSoup
# from canvas_api import make_canvas_request
import requests
import os
# from download_file import download_canvas_file

# The 'description' string from your JSON
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
    
    if not file_info or 'url' not in file_info:
        print(f"Error: Could not get download URL for {file_id}")
        return None

    download_url = file_info['url']
    filename = file_info.get('display_name', f"temp_{file_id}.pdf")
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
    
