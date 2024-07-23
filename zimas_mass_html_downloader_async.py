from bs4 import BeautifulSoup
import pandas as pd
import requests
import re
import time
import itertools
import os
import aiohttp
import asyncio


directory_path = 'zimas_html_downloads2/' #set file path to store html downloads
async_requests_per_minute = 2500

cycle_proxies_ls = None


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
  if os.path.exists(directory_path):
    # Iterate over all files in the directory
    for filename in os.listdir(directory_path):
    # Extract the pin from the filename and add it to the set
      pin, _ = os.path.splitext(filename)  # pin is the filename without the extension
      pins_downloaded_set.add(pin)

  return pins_downloaded_set



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

  else:
    return False


  return f'https://zimas.lacity.org/map.aspx?pin={pin1}{space}{pin2}&ajax=yes'



async def get_html_response(session, html_endpoint):
  """
  sends GET request to recieve zimas data in hypermedia format

  parameters:
  html_endpoint (str) - the endpoint to get data
  current_proxy (str) - proxy to use to make GET request

  returns:
  (str) - zimas data in hypermedia format in typed as a string
  """
  # proxies = {
  #  'http': 'http://' + current_proxy,
  # }
  

  #TODO: add function calls that retrieves next proxy
  global cycle_proxies_ls
  current_proxy = next(cycle_proxies_ls)
  
  proxy = 'http://' + current_proxy


  print(f"Sent GET request to {html_endpoint} response using proxy {proxy}")

    #try using old proxy script here
  async with session.get(html_endpoint) as response:
    return await response.text()



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




async def main():  



  #read in csv of all the apns, to keep track of which ones to get data from zimas for
  buildingpermits_pin_apn_df = pd.read_csv("buildingpermits_pin_apn.csv")
  # buildingpermits_pin_apn_df['downloaded'] = 0 #comment out

  start_time = time.time()
  interval = 600  # 10 minutes in seconds

  proxies_ls = get_proxies()
  global cycle_proxies_ls
  cycle_proxies_ls = itertools.cycle(proxies_ls)

  while True:
   #get next set of 300 proxies every 10 minutes
    current_time = time.time()
    if current_time - start_time >= interval:
      proxies_ls = get_proxies()
      cycle_proxies_ls = itertools.cycle(proxies_ls)
      start_time = current_time
    
    # current_proxy = next(cycle_proxies_ls)


    async_responses_ls = []
    reformatted_responses_ls = []
    pins_ls = []
    endpoints_ls = []
    
    #get set of pins already downloaded
    pins_downloaded_set = get_pins_downloaded()
    print(f"downloaded {len(pins_downloaded_set)} pins...")

    while len(pins_ls) < async_requests_per_minute:
      
      for index, row in buildingpermits_pin_apn_df.iterrows():
        if len(pins_ls) >= async_requests_per_minute:
          break

        pin = row['PIN_NBR']
        pin_parts = pin.split()
        if len(pin_parts) != 2:
          continue

        if pin in pins_downloaded_set:
          continue 

        pins_ls.append(pin)
    
    print(pins_ls)
    for pin in pins_ls:
      html_endpoint = make_html_endpoint(pin)
      endpoints_ls.append(html_endpoint)
    
    # time.sleep(30)
    print(f"retrieving endpoints...")


    
    #TODO change below to async function call -> store html responses in async_responses_ls
    # print(f"Sent GET request to {html_endpoint}")

    # async with aiohttp.ClientSession() as session:
    #   html_response = await get_html_response(session, html_endpoint, current_proxy)
    #   #html_response = get_html_response(html_endpoint, current_proxy)

    print(f"sending {async_requests_per_minute} HTML GET requests...") #WORKS HERE
    tasks = []  

    async with aiohttp.ClientSession() as session:
      # tasks = [get_html_response(session, endpoint) for endpoint in endpoints_ls]
      # async_responses_ls = await asyncio.gather(*tasks)
      for endpoint in endpoints_ls:
        tasks.append(asyncio.create_task(get_html_response(session, endpoint)))
      
      counter = 0
      for coro in asyncio.as_completed(tasks):
        html_response = await coro
        async_responses_ls.append(html_response)
        print(f"{counter} GET requests received")
        counter += 1


    print(f"reformatting {async_requests_per_minute} HTML GET requests")

    #reformat the html repsonses
    for html_response in async_responses_ls:
      html_response_reformatted = reformat_html_response(html_response)
      reformatted_responses_ls.append(html_response_reformatted)


    #save formatted html response to folder
    for i in range(len(reformatted_responses_ls)):
      pin = pins_ls[i]
      filename = directory_path + pin + ".html"
      html_response_reformatted = reformatted_responses_ls[i]
      with open(filename, "w") as file:
        file.write(html_response_reformatted)

    print(f"saved {async_requests_per_minute} files to {directory_path}")



    #reset the lists
    async_responses_ls = []
    reformatted_responses_ls = []
    pins_ls = []
    endpoints_ls = []

    time.sleep(300)


if __name__ == "__main__":
    asyncio.run(main())
