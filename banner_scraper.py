from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from multiprocessing import cpu_count
from datetime import datetime

from rule_list import get_rules

import csv
import re
import os
import time
import json
import sys 

if not os.path.exists("results"):
    os.makedirs("results")

with open('top-10k.csv', mode='r') as file:
    csvFile = csv.reader(file)
    websites = []
    for lines in csvFile:
        websites.append('https://' + lines[1] + "/")

generic_rules, domain_specific_rules = get_rules()

chrome_options = Options()
chrome_options.headless = True

#Enter path of your executable here
service = Service(executable_path='/home/ipweb/chromedriver')
possible_revocation = ['cookie preferences', 'cookie settings', 'consent manager', 'privacy settings', 'manage cookies', 'cookies settings', 'cookies preferences']

driver = webdriver.Chrome(options=chrome_options, service=service)
driver.set_page_load_timeout(10)

def scrape_url(url):
    domain = re.search(r"(?:https?://)?(?:www\.)?(.+?)/", url).group(1) #get domain name

    try:
        print("Scraping URL: " + url.strip())
        driver.get(url)
        time.sleep(15)

        current_date = datetime.now().strftime("%Y-%m-%d")
        dom = driver.page_source
        cookies = driver.get_cookies()
        local_storage = driver.execute_script("return window.localStorage;")

        #Make directory with name of webpage
        domain_dir = 'results/' + str(domain)
        if not os.path.exists(domain_dir):
            os.mkdir(domain_dir)

        with open(os.path.join(domain_dir, 'source_code.txt'), 'w') as f:
            f.write("Scraping Date - {}\n".format(current_date))
            f.write(str(dom))

        with open(os.path.join(domain_dir, 'cookies.txt'), 'w') as f:
            for cookie in cookies:
                f.write(str(cookie) + "\n")

        with open(os.path.join(domain_dir, 'local_storage.txt'), 'w') as f:
            f.write(json.dumps(local_storage))

        soup = BeautifulSoup(dom, "lxml")
        found_selectors = []

        for css_selector in tqdm(generic_rules, desc=domain, total=len(generic_rules)):
            try:
                elements = soup.select(str(css_selector))
                if len(elements) > 0:
                    found_selectors.append(css_selector)
            except KeyboardInterrupt:  
                print('Terminating Now...')  
                sys.exit(0)
            except:
                print('Ignoring selector: ' + css_selector)

        if domain in domain_specific_rules:
            for selector in domain_specific_rules[domain]:
                elements = soup.select(str(selector))
                if len(elements) > 0:
                    found_selectors.append(selector)

        if len(found_selectors) > 0:

            flag = 0
            for _str in possible_revocation:
                if( _str in dom.casefold() ):
                    flag = 1
                    text_file = open("results/banner_domain.txt", "a")
                    text_file.write(domain + ',' + str(_str) + "\n")
                    text_file.close()
                    break

            if(flag == 0):
                text_file = open("results/banner_domain.txt", "a")
                text_file.write(domain + ',' + str('None') + "\n")
                text_file.close()

    except Exception as e:
        print("There was an error accessing url:" + url)
        print(e)
        not_accessed = open("results/not_accessed.txt", "a")
        not_accessed.write(domain + "\n")
        not_accessed.close()
        print('Facing error: ' + str(e))
    except KeyboardInterrupt:  
        print('Terminating Now...')  
        sys.exit(0)

# driver = webdriver.Chrome()

# Make this thread safe and then run it
#with ThreadPoolExecutor(5) as executor:
for url in websites:
    scrape_url(url)
    #executor.submit(scrape_url, url)

driver.close()