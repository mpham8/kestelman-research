import requests
import json
import os
import pandas as pd
import urllib
import time


# Paths to the CSV file and the folder where extracted text files will be saved
csv_path = "/Users/stephaniekestelman/Dropbox (Personal)/housing_supply/LA/minutes/case_numbers_meeting_minutes.csv"
save_folder = "/Users/stephaniekestelman/Dropbox (Personal)/housing_supply/LA/entitlements/ents_minutes"


# Create a folder to save the extracted text files if it doesn't exist
os.makedirs(save_folder, exist_ok=True)

# Read the case numbers from the CSV file
case_numbers_df = pd.read_csv(csv_path)
case_numbers = case_numbers_df['x'].tolist()


# The API endpoint URL
url1 = 'https://planning.lacity.gov/pdiscaseinfo/api/Service/SearchCaseNumber'
url2 = 'https://planning.lacity.gov/pdiscaseinfo/api/Service/GetCaseInfoData'


# If there are specific headers or parameters, include them here
# In this example, I am not including any specific parameters
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Content-Type': 'application/json',
    'Referer': 'https://planning.lacity.gov/pdiscaseinfo/search/',
    'Origin': 'https://planning.lacity.gov',
    'Accept': 'application/json, text/plain, */*',
}

# Use a session to handle cookies and maintain a session
session = requests.Session()
session.headers.update(headers)


for case_number in case_numbers:
    file_path = os.path.join(save_folder, f"{case_number}_case_info.json")
    # Check if the file already exists
    if os.path.exists(file_path):
        print(
            f"File for case number {case_number} already exists. Skipping...")
        continue

    # Step 1: Search for caseId using case_number
    print(f"Searching for case number: {case_number}")

    # Step 1: Search for caseId using case_number
    try:
        with urllib.request.urlopen(f"{url1}?caseNo={case_number}") as response1:
            response1_data = json.loads(response1.read().decode())
    except Exception as e:
        print(f"Error fetching case number {case_number}: {e}")
        continue

    # Debugging: print the response data
    print(f"Response for case number {case_number}: {response1_data}")

    # Check if the response contains the caseId
    if isinstance(response1_data, list) and len(response1_data) > 0 and 'caseId' in response1_data[0]:
        case_id = response1_data[0]['caseId']

        # Wait for 1 minute before the next call
        time.sleep(60)

        # Step 2: Get case info using caseId
        try:
            with urllib.request.urlopen(f"{url2}?caseId={case_id}") as response2:
                case_info_data = json.loads(response2.read().decode())
        except Exception as e:
            print(f"Error fetching case info for case ID {case_id}: {e}")
            continue

        # Save the case info data to a file
        with open(file_path, 'w') as file:
            json.dump(case_info_data, file, indent=4)

        print(f"Data for case number {case_number} saved to {file_path}")
    else:
        print(f"No caseId found for case number {case_number}")
        # Save the blank data to a file
        with open(file_path, 'w') as file:
            case_info_data = " "
            json.dump(case_info_data, file, indent=4)

    # Wait for 2 minutes before the next call
    time.sleep(60)
