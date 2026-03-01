from canvas_api import make_canvas_request
import requests
import os

def download_canvas_file(file_id: str, save_path: str = "./"):
    """
    Uses the file_id to get a download URL and saves the file locally.
    """
    # 1. Get the file metadata
    file_info = make_canvas_request(f"/files/{file_id}")
    
    if file_info and 'url' in file_info:
        download_url = file_info['url']
        filename = file_info.get('display_name', f"file_{file_id}.pdf")
        
        # 2. Download the actual bytes
        print(f"Downloading {filename}...")
        file_res = requests.get(download_url) # S3 links usually don't need the Auth header
        
        with open(os.path.join(save_path, filename), 'wb') as f:
            f.write(file_res.content)
        print(f"Saved to {save_path}{filename}")
    else:
        print(f"Could not retrieve download URL for file ID {file_id}")