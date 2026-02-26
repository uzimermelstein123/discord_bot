from bs4 import BeautifulSoup

# The 'description' string from your JSON
def parse_assignment_description(assignment):
    html_data = assignment['description'] 
    soup = BeautifulSoup(html_data, 'html.parser')

    # Find all links that have the data-api-endpoint attribute
    for link in soup.find_all('a', attrs={'data-api-endpoint': True}):
        endpoint = link['data-api-endpoint']
        title = link.get('title', link.get('Title', 'No Title'))
        
        print(f"File Title: {title}")
        # print(f"API Endpoint: {endpoint}")
        
        # To get just the ID, split the string
        file_id = endpoint.split('/')[-1]
        print(f"Extracted File ID: {file_id}\n")