from canvas_api import get_courses, get_course_attributes
from parse_description import parse_assignment_description_for_fileid
from file_handler import download_to_server, extract_text_from_file

def process_courses():
    """
    Main orchestrator function that coordinates course processing.
    """
    courses = get_courses()
    
    if not courses:
        print("No courses to process.")
        return
    
    for course in courses:
        course_id = course.get('id')
        course_name = course.get('name', 'Unknown Course')
        print(f"\nProcessing course: {course_id} | {course_name}")
        
        assignments = get_course_attributes(course_id)
        
        for assignment in assignments:
            assignment_name = assignment.get('name', 'Unknown Assignment')
            print(f"\nProcessing assignment: {assignment_name}")
            
            # Parse assignment description to extract files
            parse_result = parse_assignment_description_for_fileid(assignment)
            
            # Download extracted files
            for file_info in parse_result['files']:
                file_path = download_to_server(
                    file_info['file_id'],
                    course_id=course_id,
                    assignment_name=assignment_name
                )
                
                if file_path:
                    extract_text_from_file(file_path)

if __name__ == "__main__":
    process_courses()
