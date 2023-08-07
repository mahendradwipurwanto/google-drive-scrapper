import requests
import json
import re

def extract_numeric_part(title):
    # This function extracts the numeric part from the file title
    match = re.search(r'\((\d+)\)', title)
    return int(match.group(1)) if match else 0

def get_files_in_folder(folder_id, api_key):
    url = f"https://www.googleapis.com/drive/v2/files?q='{folder_id}'+in+parents&key={api_key}"
    response = requests.get(url)
    data = response.json()

    result = {}
    folder_title = None
    for item in data.get("items", []):
        if item.get("mimeType") == "application/vnd.google-apps.folder":
            folder_title = item.get("title", "")
            subfolder_files = get_files_in_folder(item.get("id"), api_key)

            if folder_title not in result:
                result[folder_title] = []

            for subfolder_title, subfolder_files_list in subfolder_files.items():
                result[folder_title].extend(subfolder_files_list)
        else:
            title = item.get("title", "")
            url = item.get("webContentLink", "")
            if title and url:
                if folder_title not in result:
                    result[folder_title] = []
                result[folder_title].append({"file": title, "url": url})
                
                # Process files with .wav extension and update play URL
                if title.endswith(".wav"):
                    result[folder_title][-1]["play_url"] = url + "&play=true"

    print(f"Scrapping Page 1 with {count_data(data.get('items'))}")

    # Check if there are more pages to fetch
    page = 1
    while data.get("incompleteSearch") == False and "nextLink" in data:
        next_page_link = data["nextLink"] + f"&key={api_key}"

        page = page + 1
        response = requests.get(next_page_link)
        data = response.json()
        
        for item in data.get("items", []):
            if item.get("mimeType") == "application/vnd.google-apps.folder":
                folder_title = item.get("title", "")
                subfolder_files = get_files_in_folder(item.get("id"), api_key)

                if folder_title not in result:
                    result[folder_title] = []

                for subfolder_title, subfolder_files_list in subfolder_files.items():
                    result[folder_title].extend(subfolder_files_list)
            else:
                title = item.get("title", "")
                url = item.get("webContentLink", "")
                if title and url:
                    if folder_title not in result:
                        result[folder_title] = []
                    result[folder_title].append({"file": title, "url": url})
                    
                    # Process files with .wav extension and update play URL
                    if title.endswith(".wav"):
                        result[folder_title][-1]["play_url"] = url + "&play=true"

        print(f"Scrapping Page {page} with {count_data(data.get('items'))}")
    # Sort files in each folder by title in ascending order
    for folder_title in result:
        result[folder_title] = sorted(result[folder_title], key=lambda x: extract_numeric_part(x.get("file", "")))

    # # Sort the entire result dictionary by folder title in ascending order
    # result = {folder_title: result[folder_title] for folder_title in sorted(result.keys())}

    return result

def count_data(arr):
    total_elements = len(arr)
    return total_elements

def count_total_data(all_files):
    total_folders = len(all_files)
    total_data_points = sum(len(files_list) for files_list in all_files.values())
    return total_folders, total_data_points

def main():
    folder_id = "1o_o83msLcuW8Pc-W3rS1yQ2SECjVk5b9"
    api_key = "AIzaSyCE_u5CtItZpJVfZ__FEJKCr3UG9jD8bRA"
    output_file = "BHAGAVADGITA TERJEMAHAN 1 S-D 18.json"

    # Replace 'YOUR_FOLDER_ID' with the ID of the folder you want to start with
    # Replace 'YOUR_API_KEY' with your actual API key obtained from the Google API Console

    all_files = get_files_in_folder(folder_id, api_key)

    for folder_title, files_list in all_files.items():
        for file_info in files_list:
            if file_info["file"].endswith(".wav"):
                file_info["play_url"] = file_info["url"] + "&play=true"

    total_folders, total_data_points = count_total_data(all_files)

    # Save the result to a JSON file
    with open(output_file, "w") as f:
        json.dump(all_files, f, indent=4)

    print(f"Data scraped and saved to {output_file}.")
    print(f"Total folders: {total_folders}, Total data points (files): {total_data_points}")

if __name__ == "__main__":
    main()