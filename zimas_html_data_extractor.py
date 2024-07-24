from bs4 import BeautifulSoup
import pandas as pd
import os
import numpy as np



html_files_directory = "zimas_html_downloads2/"
html_data_directory = "zimas_html_data/"
buildingpermits_data_path = "buildingpermits_data.csv"

#create new columns (one time)
# buildingpermits_data_df["address"] = np.nan
# buildingpermits_data_df["zip_code"] = np.nan
# buildingpermits_data_df["pin_number"] = np.nan
# buildingpermits_data_df["assessor_parcel_no"] = np.nan
# buildingpermits_data_df["community_plan_area"] = np.nan
# buildingpermits_data_df["area_planning_commission"] = np.nan
# buildingpermits_data_df["neighborhood_council"] = np.nan
# buildingpermits_data_df["census_tract"] = np.nan
# buildingpermits_data_df["zoning"] = np.nan
# buildingpermits_data_df["general_plan_land_use"] = np.nan
# buildingpermits_data_df["hillside_area"] = np.nan
# buildingpermits_data_df["apn_area"] = np.nan
# buildingpermits_data_df["rent_stabilization_ordinance"] = np.nan
# buildingpermits_data_df["ellis_act_property"] = np.nan
# buildingpermits_data_df["tenant_protection_act"] = np.nan
# buildingpermits_data_df["environmental_cases"] = np.nan
# buildingpermits_data_df["city_planning_commission_cases"] = np.nan
# buildingpermits_data_df["entered_data"] = 0


def get_pins_downloaded():
  """
  gets a set of the pins of files already downloaded (pin files in prescribed folder)

  parameters:
  none

  returns
  pins_downloaded_set (set) - set of all pins downloaded already

  """
  pins_downloaded_set = set()

  # Check if the directory exists
  if os.path.exists(html_files_directory):
    # Iterate over all files in the directory
    for filename in os.listdir(html_files_directory):
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
  buildingpermits_data_df = pd.read_csv(buildingpermits_data_path)

  counter = (buildingpermits_data_df['entered_data'] == 1).sum()
  print(f"{counter} proccessed...")



  #get a set of the pins downloaded
  pins_downloaded_set = get_pins_downloaded()

  for index, row in buildingpermits_data_df.iterrows():
    pin = row['PIN_NBR']
    entered_data = row['entered_data']

    if pin not in pins_downloaded_set:
      continue

    if entered_data == 1:
       continue

    with open(html_files_directory + pin + ".html", 'r') as file:
      # Read the content of the file
      html_response = file.read()
    



    soup = BeautifulSoup(html_response, 'html.parser')
    rows = soup.find_all('tr')
    
    addresses = find_addresses(rows)
    zip_code = find_text_for_label('ZIP Code', rows)
    pin_number = find_text_for_label('PIN Number', rows)
    assessor_parcel_no = find_text_for_label('Assessor Parcel No. (APN)', rows)
    community_plan_area = find_text_for_label('Community Plan Area', rows)
    area_planning_commission = find_text_for_label('Area Planning Commission', rows)
    neighborhood_council = find_text_for_label('Neighborhood Council', rows)
    census_tract = find_text_for_label('Census Tract #', rows)
    zoning = find_text_for_label('Zoning', rows)
    general_plan_land_use = find_text_for_label('General Plan Land Use', rows)
    hillside_area = find_text_for_label('Hillside Area (Zoning Code)', rows)
    apn_area = find_text_for_label('APN Area (Co. Public Works)*', rows)
    rent_stabilization_ordinance = find_text_for_label('Rent Stabilization Ordinance (RSO)', rows)
    ellis_act_property = find_text_for_label('Ellis Act Property', rows)
    tenant_protection_act = find_text_for_label('AB 1482: Tenant Protection Act', rows)
    environmental_cases = find_multiple_text_for_label('Environmental', rows)
    city_planning_commission_cases = find_multiple_text_for_label('City Planning Commission', rows)


    buildingpermits_data_df.at[index, 'address'] = addresses
    buildingpermits_data_df.at[index, 'zip_code'] = zip_code
    buildingpermits_data_df.at[index, 'pin_number'] = pin_number
    buildingpermits_data_df.at[index, 'assessor_parcel_no'] = assessor_parcel_no
    buildingpermits_data_df.at[index, 'community_plan_area'] = community_plan_area
    buildingpermits_data_df.at[index, 'area_planning_commission'] = area_planning_commission
    buildingpermits_data_df.at[index, 'neighborhood_council'] = neighborhood_council
    buildingpermits_data_df.at[index, 'census_tract'] = census_tract
    buildingpermits_data_df.at[index, 'zoning'] = zoning
    buildingpermits_data_df.at[index, 'general_plan_land_use'] = general_plan_land_use
    buildingpermits_data_df.at[index, 'hillside_area'] = hillside_area
    buildingpermits_data_df.at[index, 'apn_area'] = apn_area
    buildingpermits_data_df.at[index, 'rent_stabilization_ordinance'] = rent_stabilization_ordinance
    buildingpermits_data_df.at[index, 'ellis_act_property'] = ellis_act_property
    buildingpermits_data_df.at[index, 'tenant_protection_act'] = tenant_protection_act
    buildingpermits_data_df.at[index, 'environmental_cases'] = environmental_cases
    buildingpermits_data_df.at[index, 'city_planning_commission_cases'] = city_planning_commission_cases
    buildingpermits_data_df.at[index, 'entered_data'] = 1


    print(f"apn {pin} processed...")
    buildingpermits_data_df.to_csv("buildingpermits_data.csv")
    counter += 1

    if counter % 10 == 0:
      print("*"*30)
      print(f"{counter} proccessed...")
      print("*"*30)

if __name__ == "__main__":
  main()