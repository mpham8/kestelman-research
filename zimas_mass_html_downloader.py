from bs4 import BeautifulSoup
import pandas as pd
import requests
import re
import time
import itertools



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


def make_html_endpoint(pin):
  """
  creates endpoint to access zimas data from pin number

  parameters:
  pin (str) - pin number

  returns:
  (str) - endpoint
  """
  pin_parts = pin.split()
  if len(pin_parts) == 2:
    pin1, pin2 = pin_parts[0], pin_parts[1]

    spaces_in_between = 0
    for i, letter in enumerate(pin):
      if letter.isspace():
        spaces_in_between += 1

    space = "%20" * spaces_in_between


  return f'https://zimas.lacity.org/map.aspx?pin={pin1}{space}{pin2}&ajax=yes'


def get_html_response(html_endpoint, current_proxy):
  """
  sends GET request to recieve zimas data in hypermedia format

  parameters:
  html_endpoint (str) - the endpoint to get data
  current_proxy (str) - proxy to use to make GET request

  returns:
  (str) - zimas data in hypermedia format in typed as a string
  """
  proxies = {
   'http': 'http://' + current_proxy,
  }
  print(f"Recieved GET request response using proxy {proxies['http']}")
  return requests.get(html_endpoint, proxies=proxies).text



def reformat_html_response(html_response):
  """
  reformats the zimas data in hypermedia format

  parameters:
  html_response (str) - zimas data in hypermedia format

  returns:
  (str) - zimas data in hypermedia format reformatted
  """

  html_response = """
  <html><head><meta http-equiv=Content-Type" content="text/html; charset=windows-1252"></head><body>
  """+ html_response
  html_response = html_response + "</body></html>"


  html_response = html_response.replace("&nbsp;", " ").replace("&lt;", "<").replace("&gt;", ">")
      
  # Fix tags by removing extra backslashes
  html_response = re.sub(r"\\>", ">", html_response)
  html_response = re.sub(r"\\<", "<", html_response)
      
  # Format the HTML content with proper indentation
  formatted_content = ""
  indentation_level = 0
  for line in html_response.splitlines():
    stripped_line = line.strip()
    if stripped_line.startswith("</"):
      indentation_level -= 1
    formatted_content += "    " * indentation_level + stripped_line + "\n"
    if stripped_line.startswith("<") and not stripped_line.startswith("</") and not stripped_line.endswith("/>"):
      indentation_level += 1
  
  return html_response




def main():  

  #read in csv of all the apns, to keep track of which ones to get data from zimas for
  buildingpermits_pin_apn_df = pd.read_csv("buildingpermits_pin_apn.csv")
  # buildingpermits_pin_apn_df['downloaded'] = 0 #comment out

  #
  start_time = time.time()
  interval = 600  # 10 minutes in seconds


  #get a list of proxies to proxy rotate (prevent zimas from timeouting requests)
  proxies_ls = get_proxies()
  cycle_proxies_ls = itertools.cycle(proxies_ls)

  #iterate through csv of all the apns
  for index, row in buildingpermits_pin_apn_df.iterrows():
    if row['downloaded'] == 1:
      continue
    
    #get next set of 300 proxies every 10 minutes
    current_time = time.time()
    if current_time - start_time >= interval:
      proxies_ls = get_proxies()
      cycle_proxies_ls = itertools.cycle(proxies_ls)
      start_time = current_time
    
    current_proxy = next(cycle_proxies_ls)

    pin = row['PIN_NBR']
    html_endpoint = make_html_endpoint(pin)
    print(f"Sent GET request to {html_endpoint}")
    html_response = get_html_response(html_endpoint, current_proxy)
    # print(html_response)


    #save formatted html response to folder
    html_response_reformatted = reformat_html_response(html_response)
    filename = "zimas_html_downloads/" + pin + ".html"
    with open(filename, "w") as file:
      file.write(html_response_reformatted)

    buildingpermits_pin_apn_df.at[index, 'downloaded'] = 1 #once apn is downloaded, mark as downloaded in the csv
    buildingpermits_pin_apn_df.to_csv('buildingpermits_pin_apn.csv') #update the csv 

    # time.sleep(0.08)


main()