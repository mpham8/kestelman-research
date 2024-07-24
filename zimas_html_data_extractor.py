from bs4 import BeautifulSoup
import os
import csv


html_files_directory = "zimas_html_downloads2/"
html_data_directory = "zimas_html_data/"


def get_pins_downloaded(files_directory):
  """
  gets a set of the pins of files already downloaded/processed (pin files in prescribed folder)

  parameters:
  files_directory - which directory to check

  returns
  pins_downloaded_set (set) - set of all pins downloaded already

  """
  pins_downloaded_set = set()

  # Check if the directory exists
  if os.path.exists(files_directory):
    # Iterate over all files in the directory
    for filename in os.listdir(files_directory):
    # Extract the pin from the filename and add it to the set
      pin, _ = os.path.splitext(filename)  # pin is the filename without the extension
      pins_downloaded_set.add(pin)

  return pins_downloaded_set


def find_text_for_label(label, rows):
    """
    Finds and returns the text associated with a specific label from the given rows.

    Parameters:
    label (str) - The label to search for in the rows.
    rows (list) - List of HTML table rows to search for the label.

    Returns:
    text (str) - Text associated with the given label, or None if the label is not found.
    """
    for row in rows:
        cells = row.find_all('td')
        if cells and label in cells[0].get_text(strip=True):
            return cells[1].get_text(strip=True)
    return None



def find_addresses(rows):
    """
    Finds and returns the addresses from the given rows.

    Parameters:
    rows (list) - List of HTML table rows to search for addresses.

    Returns:
    addresses_as_string (str) - Concatenated string of all addresses found in the rows.
    """
    addresses = []
    for row in rows:
        cells = row.find_all('td')
        if cells and 'Site Address' in cells[0].get_text(strip=True):
            addresses.append(cells[1].get_text(strip=True))
        addresses_as_string = ' '.join(addresses)
        return addresses_as_string


def find_multiple_text_for_label(label, rows):
    cases = []
    # div_tab5 = soup.find(text=lambda text: text and 'divTab5:' in text)
    for row in rows:
        cells = row.find_all('td')
        if cells and label in cells[0].get_text(strip=True):
            if len(cells) <= 1:
                break
            case = cells[1].get_text(strip=True)
            cases.append(case)
    cases_as_string = ' '.join(cases)
    return cases_as_string


def main():

  #get a set of the pins downloaded
  pins_downloaded_set = get_pins_downloaded(html_files_directory)
  pins_proccessed_set = get_pins_downloaded(html_data_directory)

  total_pins = len(pins_downloaded_set)

  for pin in pins_downloaded_set:
    
    pins_proccessed_set = get_pins_downloaded(html_data_directory)
    if pin not in pins_downloaded_set:
      continue
    if pin in pins_proccessed_set:
       continue


    with open(html_files_directory + pin + ".html", 'r') as file:
      # Read the content of the file
      html_response = file.read()
    

    soup = BeautifulSoup(html_response, 'html.parser')
    rows = soup.find_all('tr')

    #create csv data structure
    data = {
        "pin": pin,
        "addresses": find_addresses(rows),
        "zip_code": find_text_for_label('ZIP Code', rows),
        "pin_number": find_text_for_label('PIN Number', rows),
        "assessor_parcel_no": find_text_for_label('Assessor Parcel No. (APN)', rows),
        "community_plan_area": find_text_for_label('Community Plan Area', rows),
        "area_planning_commission": find_text_for_label('Area Planning Commission', rows),
        "neighborhood_council": find_text_for_label('Neighborhood Council', rows),
        "census_tract": find_text_for_label('Census Tract #', rows),
        "zoning": find_text_for_label('Zoning', rows),
        "general_plan_land_use": find_text_for_label('General Plan Land Use', rows),
        "hillside_area": find_text_for_label('Hillside Area (Zoning Code)', rows),
        "apn_area": find_text_for_label('APN Area (Co. Public Works)*', rows),
        "rent_stabilization_ordinance": find_text_for_label('Rent Stabilization Ordinance (RSO)', rows),
        "ellis_act_property": find_text_for_label('Ellis Act Property', rows),
        "tenant_protection_act": find_text_for_label('AB 1482: Tenant Protection Act', rows),
        "environmental_cases": find_multiple_text_for_label('Environmental', rows),
        "city_planning_commission_cases": find_multiple_text_for_label('City Planning Commission', rows)
    }

    csv_file_path = html_data_directory + pin + ".csv"

    #export to csv
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        writer.writeheader()
        writer.writerow(data)

    #CLI output
    print(f"apn {pin} processed...")
    pins_proccessed = len(pins_proccessed_set)
    if pins_proccessed % 10 == 0:
      print("*"*30)
      print(f"{pins_proccessed}/{total_pins} proccessed...")
      print("*"*30)

    pins_proccessed_set.add(pin)

if __name__ == "__main__":
  main()