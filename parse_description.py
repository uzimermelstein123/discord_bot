from bs4 import BeautifulSoup
import os
import re

def parse_assignment_description_for_fileid(assignment):
    """
    Parses assignment description to extract file IDs.
    If no files with data-api-endpoint are found, saves the HTML description.
    :param assignment: The assignment object from Canvas API
    :return: Dictionary with 'files' list and 'html_content'
    """
    html_data = assignment.get('description', '')
    assignment_name = assignment.get('name', 'unknown_assignment')
    
    if not html_data:
        print("No description found in assignment.")
        return {'files': [], 'html_content': None}
    
    soup = BeautifulSoup(html_data, 'html.parser')
    extracted_files = []
    
    # Find all links that have the data-api-endpoint attribute
    links_with_endpoint = soup.find_all('a', attrs={'data-api-endpoint': True})
    
    # If links with data-api-endpoint exist, extract them
    if links_with_endpoint:
        for link in links_with_endpoint:
            endpoint = link['data-api-endpoint']
            title = link.get('title', link.get('Title', 'No Title'))
            file_id = endpoint.split('/')[-1]
            
            extracted_files.append({
                'file_id': file_id,
                'title': title
            })
            print(f"File Title: {title}, File ID: {file_id}")
    else:
        # No files found, save HTML content
        print("No files with data-api-endpoint found in assignment description.")
        # save_html_content(assignment_name, html_data)
    
    return {
        'files': extracted_files,
        'html_content': html_data,
        'assignment_name': assignment_name
    }

def save_html_content(assignment_name, html_content, output_folder="./assignments"):
    """
    Saves HTML content to a file.
    :param assignment_name: The name of the assignment
    :param html_content: The HTML content to save
    :param output_folder: The folder where the file will be saved
    """
    os.makedirs(output_folder, exist_ok=True)
    sanitized_name = re.sub(r'(?u)[^-\w.]', '_', assignment_name)
    file_path = os.path.join(output_folder, f"{sanitized_name}_desc.txt")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Saved HTML description to: {file_path}\n")

# if __name__ == "__main__":
    # Example usage with a mock assignment object
    # mock_id = 
    # result = parse_assignment_description_for_fileid(mock_assignment)
    # print(result)