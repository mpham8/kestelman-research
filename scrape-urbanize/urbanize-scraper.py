from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from time import sleep
# from login import EMAIL
# from login import PASSWORD
# from login import LINK
from savedfeb25 import DOWNLOADED_SET
import re
import requests
from IPython.display import Image, display
import os
import csv
import sys


#save data to this folder
data_save_folder = "data-feb25run"


def boot_and_login(LINK):
    """
    boot selenium driver and login
    params:
        none
    return:
        driver (selenium driver)
        wait (selenium wait)
    """
    driver = webdriver.Firefox()
    wait = WebDriverWait(driver, 10)
    driver.maximize_window()

    driver.get(LINK)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))


    # driver.get("https://pro.urbanize.city/users/sign_in")

    # wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))


    # iframes = driver.find_elements(By.TAG_NAME, "iframe")
    # if iframes:
    #     driver.switch_to.frame(iframes[0])

    # email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='email'], input[type='email']")))
    # email_input.send_keys(EMAIL)

    # password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password'], input[type='password']")))
    # password_input.send_keys(PASSWORD)

    # login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.prime[actionlogin]")))
    # login_button.click()


    # wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # driver.switch_to.default_content()
    # wait.until(EC.visibility_of_element_located((By.XPATH, "//a[contains(@class, 'border-cyan-500') and contains(text(), 'Dashboard')]")))


    return driver, wait



def get_project_info(driver, wait, url):
  """
  get project data for individual project
  params:
    driver
    wait
    url (str) - project page url
  return:
    project_info_dict (dictionary) - hashmap with project info
  """
  driver.get(url)

  #get project name
  wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
  project_name = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.text-5xl.font-semibold.text-gray-900.tracking-tight.mb-2"))).text

  print(f"Project Name: {project_name}")
  

  #get project status
  status = None
  status_elements = driver.find_elements(By.CSS_SELECTOR, "div.flex.space-x-1.w-full > div")
  for element in status_elements:
    bg_div = element.find_element(By.CSS_SELECTOR, "div[class*='w-full'][class*='h-2.5']")
    if "bg-cyan-600" in bg_div.get_attribute("class"):
      status = element.find_element(By.CSS_SELECTOR, "div.text-sm").text

  print(f"Project Status: {status}")


  #get location
  location_header = driver.find_element(By.XPATH, "//h3[contains(@class, 'text-xl') and contains(text(), 'Location')]")
  location_html = location_header.find_element(By.XPATH, "following-sibling::p").get_attribute('innerHTML')
  # location_text = location_element2.text.replace('\n', ', ')
  location_text = re.sub('<[^<]+?>', '', location_html).replace('\n', '').strip()
  # location_text = ', '.join(part.strip() for part in location_text.split(','))

  print(f"Project Location: {location_text}")


  companies = {}
  try:
      companies_div = driver.find_element(By.XPATH, "//h3[contains(@class, 'text-xl') and contains(text(), 'Companies')]/ancestor::div[contains(@class, 'project-companies')]")
      company_items = companies_div.find_elements(By.XPATH, ".//li[contains(@class, 'py-2')]")
      
      for item in company_items:
          label = item.find_element(By.XPATH, ".//div[contains(@class, 'text-slate-900') and contains(@class, 'font-medium')]").text
          value_div = item.find_element(By.XPATH, ".//div[contains(@class, 'space-y-1')]")
          company_elements = value_div.find_elements(By.CSS_SELECTOR, "div.text-cyan-600.font-semibold a")
          companies[label] = [element.text for element in company_elements]
          print(f"{label}: {', '.join(companies[label])}")
  except:
      print("Companies section not found or could not be parsed")

  project_info = {}
  try:
        information_div = driver.find_element(By.XPATH, "//h3[contains(@class, 'text-xl') and contains(text(), 'Information')]/ancestor::div[contains(@class, '')]")
        info_items = information_div.find_elements(By.XPATH, ".//li[contains(@class, 'py-4')]")
        
        for item in info_items:
            label = item.find_element(By.XPATH, ".//div[contains(@class, 'text-slate-900') and contains(@class, 'font-medium')]").text
            value_div = item.find_element(By.XPATH, ".//div[contains(@class, 'text-slate-800') and contains(@class, 'font-normal')]")
            
            if label == "Project uses":
                uses = [use.text for use in value_div.find_elements(By.XPATH, ".//div/div")]
                project_info[label] = uses
                print(f"Project uses: {', '.join(uses)}")
            else:
                value = value_div.text.strip()
                project_info[label] = value
                print(f"{label}: {value}")
  except:
        print("Information section not found or could not be parsed")

    # Return the extracted data as a dictionary
  result = {
        "project_name": project_name,
        "status": status,
        "location": location_text,
        **companies,
        **project_info
    }
    
  print(result)

  return result



def get_article_info(driver, wait, url, article_folder):
  """
  get article data for individual article
  params:
    driver (selenium driver)
    wait (selenium wait)
    url (str) - article page url
    article_folder (str) - folder location to save article data
  return:
    article_title (str) - article title
    article_subtitle (str) - article subtitle
    article_body (str) - article body
    image_urls (list) - list of image urls
    comment_data (dict) - hashmap with comment data
  """
  driver.get(url)

  wait.until(EC.presence_of_element_located((By.CLASS_NAME, "article-lead-image")))

  #get lead image
  lead_image_div = driver.find_element(By.CLASS_NAME, "article-lead-image")
  lead_image = lead_image_div.find_element(By.TAG_NAME, "img")
  lead_image_url = lead_image.get_attribute('src')

  image_urls = [lead_image_url] if lead_image_url else []

  
  wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

  #get other images
  images = driver.find_elements(By.XPATH, "//img[@class='image-950w article-inline-image']")
  
  for image in images:
      src = image.get_attribute('src')
      if src:
          image_urls.append(src)
  

  #get h1 class = "article-title"
  article_title = driver.find_element(By.CSS_SELECTOR, "h1.article-title").text

  #get h2 class = " article-subtitle"
  try:
      article_subtitle = driver.find_element(By.CSS_SELECTOR, "h2.article-subtitle").text
  except:
      article_subtitle = ""

  #get article date
  article_date = driver.find_element(By.CSS_SELECTOR, "div.article-byline").text.split('Comments')[0].strip()
  article_date = article_date.split(',')[0] + ',' + article_date.split(',')[1]


  #get p in class="article-body"
  article_body_div = driver.find_element(By.CSS_SELECTOR, "div.article-body")
  paragraphs = article_body_div.find_elements(By.CSS_SELECTOR, "p:not(.image-and-caption)")
  article_body = "\n".join([p.text for p in paragraphs])


  #get comment    
  wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
    
  #switch to  iframe
  iframe = driver.find_element(By.TAG_NAME, "iframe")
  driver.switch_to.frame(iframe)
    
  try:
      wait.until(EC.presence_of_element_located((By.ID, "post-list")))
  except:
      # Do something else if "post-list" is not found
      print("No comments found for this article.")
      # driver.switch_to.default_content()

  comments = driver.find_elements(By.CSS_SELECTOR, "li.post")
    
  comment_data = []
    
  for comment in comments:
        comment_id = comment.get_attribute("id")
        author = comment.find_element(By.CSS_SELECTOR, "span.author").text
        content = comment.find_element(By.CSS_SELECTOR, "div.post-message").text
        timestamp = comment.find_element(By.CSS_SELECTOR, "a.time-ago").get_attribute("title")
        
        parent_link = comment.find_elements(By.CSS_SELECTOR, "a.parent-link")
        parent_id = parent_link[0].get_attribute("href").split("#")[-1] if parent_link else None
        
        comment_data.append({
            "id": comment_id,
            "author": author,
            "content": content,
            "timestamp": timestamp,
            "parent_id": parent_id
        })
    
    # driver.switch_to.default_content()

  article_image_folder = os.path.join(article_folder, "images")
  os.makedirs(article_image_folder, exist_ok=True)

  print("Article Title:", article_title)
  print("Article Subtitle:", article_subtitle)
  print("Article Date", article_date)
  print("Article Body:", article_body)
  for i, image_url in enumerate(image_urls, 1):
    response = requests.get(image_url)
    if response.status_code == 200:
      print(f"Image {i}: {image_url}")

      image_filename = f"image_{i}.jpg"
      image_path = os.path.join(article_image_folder, image_filename)
      with open(image_path, 'wb') as f:
          f.write(response.content)
      # print(f"Image {i} saved as: {image_path}")
      # display(Image(response.content))
  print("Comments:", comment_data)
    
  return article_title, article_subtitle, article_date, article_body, image_urls, comment_data



def get_page_project_urls(driver):
  """
  get project urls for each page under "projects"
  params:
    driver (selenium driver)
  return:
    page_urls (list) - list of project urls
  """
  project_links = driver.find_elements(By.CSS_SELECTOR, "ul.grid a[href^='/los_angeles/projects/']")
  page_urls = [link.get_attribute('href') for link in project_links]

  return page_urls

def get_project_data(driver, wait, url):
  """
  get project data, all articles and comments for individual project, then saves data to csv
  params:
    driver (selenium driver)
    wait (selenium wait)
    url (str) - project page url
  return:
    none
  """
  driver.get(url)

  # Extract the last two parts of the URL
  url_parts = url.rstrip('/').split('/')
  last_two_parts = '_'.join(url_parts[-2:])
  project_id = last_two_parts.replace('/', '_')
  
  # print(f"Extracted project ID: {project_id}")

  wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    
  project_name = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.text-5xl.font-semibold.text-gray-900.tracking-tight.mb-2"))).text

  # project_data[url]['project_name'] = project_name
  print("*"*21)
  print("PROJECT NAME:", project_name)
  print("PROJECT ID:", project_id)
  print("*"*21)

  project_info_dict = get_project_info(driver, wait, url)

  # Export project info to CSV
  project_folder = os.path.join(data_save_folder, project_id)
  os.makedirs(project_folder, exist_ok=True)

  csv_filename = os.path.join(data_save_folder, project_id, f"projectinfo.csv")
  with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
      writer = csv.DictWriter(csvfile, fieldnames=project_info_dict.keys())
      writer.writeheader()
      writer.writerow(project_info_dict)
  # print(f"Project info exported to {csv_filename}")



  articles_folder = os.path.join(data_save_folder, project_id, "articles")
  os.makedirs(articles_folder, exist_ok=True)

  #get article urls for each project
  grid_exists = len(driver.find_elements(By.CSS_SELECTOR, "ul.grid")) > 0

  if grid_exists:
      grid_links = driver.find_elements(By.CSS_SELECTOR, "ul.grid li a")
      grid_urls = [link.get_attribute('href') for link in grid_links]
      # project_data[url]['grid_urls'] = grid_urls
      for article_url in grid_urls:
         #get article data(article url)

        # Extract the last part of the article URL
        article_id = article_url.rstrip('/').split('/')[-1]
        article_folder = os.path.join(data_save_folder, project_id, "articles", article_id)
        os.makedirs(article_folder, exist_ok=True)
        
        article_title, article_subtitle, article_date, article_body, image_urls, comment_data = get_article_info(driver, wait, article_url, article_folder)

        article_csv_filename = os.path.join(article_folder, f"articleinfo.csv")
        article_info = {
            'title': article_title,
            'subtitle': article_subtitle,
            'date': article_date,
            'body': article_body
        }
        with open(article_csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=article_info.keys())
            writer.writeheader()
            writer.writerow(article_info)

        # Export comment data to CSV
        comment_csv_filename = os.path.join(article_folder, f"comments.csv")
        if comment_data:
            with open(comment_csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=comment_data[0].keys())
                writer.writeheader()
                for comment in comment_data:
                    writer.writerow(comment)



def main():
  # page_number = 176
  seen_all = False

  # Get command line arguments  
  if len(sys.argv) == 3:
      LINK = sys.argv[1]
      page_number = int(sys.argv[2])
  elif len(sys.argv) == 2:
      LINK = sys.argv[1]
      page_number = 0

  print(LINK)

  driver, wait = boot_and_login(LINK)


  downloaded_set = DOWNLOADED_SET

  driver.get("https://pro.urbanize.city/los_angeles/projects")

  # # # click the login button
  # login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.rounded-full.bg-cyan-600[data-action='click->login#login']")))
  # login_button.click()

  # Wait for 5 seconds after clicking
  sleep(5)


  while seen_all == False:
    #go to next page
    page_number += 1
    driver.get(f"https://pro.urbanize.city/los_angeles/projects?page={page_number}")

    #get project url from each page
    page_urls = get_page_project_urls(driver)
    project_data = {url: {} for url in page_urls}


    

    #for each url get the project info
    for url in page_urls:
      
      if url in downloaded_set:
            print(f"Project {url} already downloaded")
            continue
      #TO DO: check if project is already downloaded
      get_project_data(driver, wait, url)

      # Update the downloaded set with the current URL
      downloaded_set.add(url)

      # Write the updated downloaded set to the downloaded.py file
      with open('savedfeb25.py', 'w') as f:
          f.write(f"DOWNLOADED_SET = {repr(downloaded_set)}\n")


if __name__ == "__main__":
    main()
