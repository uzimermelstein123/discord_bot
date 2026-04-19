from canvas_api import get_courses, get_course_attributes
from parse_description import parse_assignment_description_for_fileid
from file_handler import download_to_server, extract_text_from_file
import os

def process_courses():
    """
    Main orchestrator function that coordinates course processing.
    """
    courses = get_courses()
    
    if not courses:
        print("No courses to process.")
        return
    
    for course in courses:  # Filter for Spring 2024 courses
        if course["enrollment_term_id"] == 1: # If default course skip
            continue
        course_id = course.get('id')
        course_name = course.get('name', 'Unknown Course')
        print(f"\nProcessing course: {course_id} | {course_name}")
        
        # Create course folder using course name
        course_folder = os.path.join("./assignments", course_name)
        os.makedirs(course_folder, exist_ok=True)
        
        assignments = get_course_attributes(course_id)
        
        for assignment in assignments:
            assignment_name = assignment.get('name', 'Unknown Assignment')
            print(f"\nProcessing assignment: {assignment_name}")
            
            # Create assignment folder within course folder
            assignment_folder = os.path.join(course_folder, assignment_name)
            os.makedirs(assignment_folder, exist_ok=True)
            
            # Parse assignment description to extract files
            parse_result = parse_assignment_description_for_fileid(assignment)
           
            if 'files' in parse_result and parse_result['files']:
                for file_info in parse_result['files']:
                    file_path = download_to_server(
                        file_info['file_id'],
                        output_folder=assignment_folder
                    )
                    
                    if file_path:
                        extract_text_from_file(file_path, output_folder=assignment_folder)
            
            # Handle HTML content if no files found
            if 'html_content' in parse_result and parse_result['html_content']:
                html_file = os.path.join(assignment_folder, 'assignment_description.html')
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(parse_result['html_content'])
                print(f"Saved HTML description to: {html_file}")


if __name__ == "__main__":
    process_courses()
