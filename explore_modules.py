"""
Test download script for Canvas modules.
Extracts URLs by item type and saves content organized by:
  test_folder/{course_name}/{module_name}/{item}
"""
import os
import json
import re
import requests
from dotenv import load_dotenv
from canvas_api import get_courses, make_canvas_request
from file_handler import download_to_server, extract_text_from_file

load_dotenv()
CANVAS_API_URL = os.getenv("CANVAS_API_URL", "")
CANVAS_API_KEY = os.getenv("CANVAS_API_KEY", "")
TEST_FOLDER = "./test_folder"


def sanitize(name):
    """Remove characters invalid in folder/file names."""
    return re.sub(r'[\\/*?:"<>|]', '_', name).strip()


def process_item(item, module_folder):
    item_type = item.get("type", "Unknown")
    title = sanitize(item.get("title", "Untitled"))

    if item_type == "SubHeader":
        return

    elif item_type == "File":
        content_id = item.get("content_id")
        if not content_id:
            print(f"      [File] No content_id found, skipping.")
            return
        file_path = download_to_server(content_id, output_folder=module_folder)
        if file_path:
            extract_text_from_file(file_path, output_folder=module_folder)

    elif item_type == "ExternalUrl":
        external_url = item.get("external_url", "")
        html_url = item.get("html_url", "")

        if external_url:
            download_url = external_url
            use_auth = False  # SharePoint / external — no Canvas auth
        elif html_url:
            separator = "&" if "?" in html_url else "?"
            download_url = f"{html_url}{separator}download_frd=1"
            use_auth = True
        else:
            print(f"      No url available for ExternalUrl '{title}', skipping.")
            return

        headers = {"Authorization": f"Bearer {CANVAS_API_KEY}"} if use_auth else {}

        # For SharePoint URLs, reuse browser cookies from the local Chrome session
        cookies = None
        if not use_auth and "sharepoint.com" in download_url:
            try:
                import browser_cookie3
                cookies = browser_cookie3.chrome(domain_name=".sharepoint.com")
                print(f"      Using Chrome SharePoint cookies for '{title}'.")
            except Exception as e:
                print(f"      Warning: Could not load browser cookies ({e}). Trying without.")

        try:
            response = requests.get(
                download_url,
                headers=headers,
                cookies=cookies,
                stream=True,
                allow_redirects=True,
            )
            response.raise_for_status()

            # Determine filename from Content-Disposition or final URL
            content_disposition = response.headers.get("Content-Disposition", "")
            cd_match = re.search(r'filename="?([^";\n]+)"?', content_disposition)
            if cd_match:
                filename = sanitize(cd_match.group(1).strip())
            else:
                # Fall back to last segment of final URL
                final_url = response.url
                url_filename = final_url.split("?")[0].rstrip("/").split("/")[-1]
                filename = sanitize(url_filename) if url_filename else f"{title}.bin"

            out_file = os.path.join(module_folder, filename)
            with open(out_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"      Downloaded ExternalUrl → {out_file}")
            extract_text_from_file(out_file, output_folder=module_folder)
        except requests.exceptions.RequestException as e:
            print(f"      Failed to download ExternalUrl '{title}': {e}")
            # raise SystemExit(1)

    elif item_type in ("Page", "Discussion", "Assignment"):
        # api_url (item["url"]) returns JSON with full content
        api_url = item.get("url", "")
        if not api_url:
            print(f"      [{item_type}] No api_url found, skipping.")
            return
        endpoint = api_url.replace(CANVAS_API_URL, "")
        data = make_canvas_request(endpoint)
        if data:
            out_file = os.path.join(module_folder, f"{title}.json")
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"      Saved {item_type} → {out_file}")
            if item_type == "Assignment":
                print(f"      NOTE: Assignment may have new_window behavior to investigate later.")
    else:
        print(f"      [{item_type}] Unhandled type — skipping.")


def explore_modules():
    # courses = get_courses()
    # if not courses:
    #     print("No courses found.")
    #     return

    # for course in courses:
    #     if course.get("enrollment_term_id") == 1:
    #         continue

    #     course_id = course["id"]
    #     course_name = sanitize(course.get("name", "Unknown"))
    #     print(f"\n{'='*60}")
    #     print(f"COURSE: {course_name} (ID: {course_id})")
    #     print(f"{'='*60}")
        course_name = "COT 2000C"
        course_id = 192086 # Testing this course
        modules = make_canvas_request(f"/api/v1/courses/{course_id}/modules")
        if not modules:
            print("  No modules found.")
            # continue

        for module in modules:
            module_name = sanitize(module.get("name", "Unknown"))
            module_folder = os.path.join(TEST_FOLDER, course_name, module_name)
            os.makedirs(module_folder, exist_ok=True)

            print(f"\n  MODULE: {module_name}")
            print(f"  Folder: {module_folder}")

            items_url = module.get("items_url", "")
            if not items_url:
                print("    (no items URL)")
                continue

            endpoint = items_url.replace(CANVAS_API_URL, "")
            items = make_canvas_request(endpoint)
            if not items:
                print("    (no items)")
                continue

            for item in items:
                item_type = item.get("type", "Unknown")
                title = item.get("title", "Untitled")
                print(f"    [{item_type}] {title}")
                process_item(item, module_folder)


if __name__ == "__main__":
    explore_modules()
