import requests
import json
import os
import pandas as pd
import time

import pandas as pd
import requests
import time
import itertools
import os


# Paths to the CSV file and the folder where extracted text files will be saved
csv_path = "case_numbers_meeting_minutes.csv"
directory_path = "cases/"

cycle_proxies_ls = None


def get_cases_downloaded():
  """
  gets a set of the pins of files already downloaded (pin files in prescribed folder)

  parameters:
  none

  returns
  cases_downloaded_set (set) - set of all pins downloaded already

  """
  cases_downloaded_set = set()

  # Check if the directory exists
  if os.path.exists(directory_path):
    # Iterate over all files in the directory
    for filename in os.listdir(directory_path):
    # Extract the pin from the filename and add it to the set
      case, _ = os.path.splitext(filename)  # pin is the filename without the extension
      cases_downloaded_set.add(case)

  return cases_downloaded_set


def get_proxies():
  """
  scrapes website to get a list of usable proxies

  parameters:
  none

  returns:
  (list) - list of 300 proxies
  """
  response = requests.get('https://free-proxy-list.net/') 
  df = pd.read_html(response.text)[0]
  proxies_ls = df['IP Address'].tolist()

  return proxies_ls


def get_response(endpoint, current_proxy):
  """
  sends GET request to recieve zimas data in json format

  parameters:
  endpoint (str) - the endpoint to get json data
  current_proxy (str) - proxy to use to make GET request

  returns:
  (str) - zimas data in json format in typed as a string
  """
  proxies = {
   'http': 'http://' + current_proxy,
  }
  print(f"Recieved GET request response using proxy {proxies['http']}")
  return requests.get(endpoint, proxies=proxies).json()



def main():
    #get set of pins already downloaded
    cases_downloaded_set = get_cases_downloaded()
    print(f"downloaded {len(cases_downloaded_set)} cases...")

    # Read the case numbers from the CSV file
    case_numbers_df = pd.read_csv(csv_path)
    case_numbers = case_numbers_df['x'].tolist()

    start_time = time.time()
    interval = 600  # 10 minutes in seconds

    proxies_ls = get_proxies()
    global cycle_proxies_ls
    cycle_proxies_ls = itertools.cycle(proxies_ls)

    for case in case_numbers:
        case_file_name = case + "_case_info"
        full_case_file_name = directory_path + case_file_name + ".json"

        if case_file_name in cases_downloaded_set:
            continue
        
        #get next set of 300 proxies every 10 minutes
        current_time = time.time()
        if current_time - start_time >= interval:
            proxies_ls = get_proxies()
            cycle_proxies_ls = itertools.cycle(proxies_ls)
            start_time = current_time

        # The API endpoint URL
        endpoint1 = f"https://planning.lacity.gov/pdiscaseinfo/api/Service/SearchCaseNumber?caseNo={case}"
        
        print(f"Sent GET request to {endpoint1} to get case id...")

        current_proxy = next(cycle_proxies_ls)
        json_response = get_response(endpoint1, current_proxy)

        # print(json_response)

        if isinstance(json_response, list) and len(json_response) > 0 and 'caseId' in json_response[0]:
            case_id = json_response[0]['caseId']
            print("Case id found in json response")
        else:
            with open(full_case_file_name, 'w') as file:
                case_info_data = " "
                json.dump(case_info_data, file, indent=4)
            continue
        
        print(f"Sent GET request to {endpoint1} to get case info...")
        endpoint2 = f"https://planning.lacity.gov/pdiscaseinfo/api/Service/GetCaseInfoData?caseId={case_id}"
        print(f"Sent GET request to {endpoint2}")
        
        current_proxy = next(cycle_proxies_ls)
        json_response = get_response(endpoint2, current_proxy)

        # Save the case info data to a file
        with open(full_case_file_name, 'w') as file:
            json.dump(json_response, file, indent=4)


        print(f"Data for case number {case} saved to {directory_path}")



if __name__ == "__main__":
    main()

