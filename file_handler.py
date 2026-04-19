import requests
import os
import re
import mimetypes
import pdfplumber
from docx import Document
from bs4 import BeautifulSoup
from canvas_api import make_canvas_request

def download_to_server(file_id, output_folder="./assignments", course_id=None, assignment_name=None):
    """
    Downloads a file from Canvas API.
    :param file_id: The ID of the file to download
    :param output_folder: The base folder where files will be saved (default: "./assignments")
    :param course_id: Optional course ID for organized folder structure
    :param assignment_name: Optional assignment name for organized folder structure
    :return: The path to the downloaded file or None if failed
    """
    file_info = make_canvas_request(f"/api/v1/files/{file_id}")

    if not file_info or 'url' not in file_info:
        print(f"Error: Could not get download URL for {file_id}")
        return None

    download_url = file_info['url']
    filename = file_info.get('display_name', f"temp_{file_id}.pdf")
    
    if course_id and assignment_name:
        output_folder = os.path.join(output_folder, str(course_id), assignment_name)
    
    save_path = os.path.join(output_folder, filename)

    os.makedirs(output_folder, exist_ok=True)

    print(f"Downloading {filename}...")
    try:
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        print(f"File stored at: {save_path}")
        return save_path
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return None

def extract_text_from_file(file_path, output_folder=None):
    """
    Extracts text from PDF or DOCX files.
    :param file_path: The path to the file
    :param output_folder: Optional folder where extracted text will be saved. If None, uses the directory of the input file.
    :return: The path to the extracted text file or None if failed
    """
    if output_folder is None:
        output_folder = os.path.dirname(file_path)
    
    os.makedirs(output_folder, exist_ok=True)
    file_extension = file_path.lower().split('.')[-1]

    if file_extension == 'pdf':
        return _extract_from_pdf(file_path, output_folder)
    elif file_extension == 'docx':
        return _extract_from_docx(file_path, output_folder)
    else:
        print(f"Error: The file '{file_path}' is not a supported file type (PDF or DOCX).\n")
        return None

def _extract_from_pdf(file_path, output_folder):
    """
    Extracts text from a PDF file.
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type != 'application/pdf':
        print(f"Error: The file '{file_path}' is not a valid PDF (MIME type: {mime_type}).")
        return None

    try:
        with pdfplumber.open(file_path) as pdf:
            if not pdf.pages:
                print(f"Error: The file '{file_path}' has no pages.")
                return None

            print(f"Extracting text from PDF '{file_path}'...")
            pages_text = []
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                pages_text.append(f"Page {i + 1}:\n{page_text}")

            output_file = os.path.join(output_folder, os.path.basename(file_path).replace('.pdf', '.txt'))
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(pages_text))
            print(f"Extracted text saved to: {output_file}\n")
            return output_file
    except Exception as e:
        print(f"Error processing PDF file '{file_path}': {e}\n")
        return None

def _extract_from_docx(file_path, output_folder):
    """
    Extracts text from a DOCX file.
    """
    try:
        doc = Document(file_path)
        print(f"Extracting text from DOCX '{file_path}'...")
        extracted_text = ""

        for paragraph in doc.paragraphs:
            extracted_text += paragraph.text + "\n"

        output_file = os.path.join(output_folder, os.path.basename(file_path).replace('.docx', '.txt'))
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(extracted_text)
        print(f"Extracted text saved to: {output_file}\n")
        return output_file
    except Exception as e:
        print(f"Error processing DOCX file '{file_path}': {e}\n")
        return None


def extract_text_from_canvas_json(data: dict, item_type: str, output_folder: str, title: str):
    """
    Extracts HTML content from a saved Canvas JSON object and writes plain text.
    Assignment → description field, Page → body field, Discussion → message field.
    """
    field_map = {"Assignment": "description", "Page": "body", "Discussion": "message"}
    field = field_map.get(item_type)
    if not field:
        return None

    html = data.get(field, "") or ""
    if not html.strip():
        print(f"  [{item_type}] No {field} content to extract.")
        return None

    text = BeautifulSoup(html, "html.parser").get_text(separator="\n").strip()
    safe_title = re.sub(r'[\\/*?:"<>|]', '_', title)
    out_file = os.path.join(output_folder, f"{safe_title}.txt")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"  Extracted text → {out_file}")
    return out_file
