from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup
from tqdm import tqdm

from rule_list import get_rules

import csv
import re
import os

if not os.path.exists("results/screenshots"):
    os.makedirs("results")
    os.makedirs("results/screenshots")

with open('top-10k.csv', mode='r') as file:
    csvFile = csv.reader(file)
    websites = []
    for lines in csvFile:
        websites.append('https://' + lines[1] + "/")

generic_rules, domain_specific_rules = get_rules()

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

# driver = webdriver.Chrome()
for url in websites:

    domain = re.search(r"(?:https?://)?(?:www\.)?(.+?)/", url).group(1) #get domain name

    try:
        driver.set_page_load_timeout(10)
        print("Scraping URL: " + url.strip())
        driver.get(url)
        driver.implicitly_wait(3)

        dom = driver.page_source

        soup = BeautifulSoup(dom, "lxml")
        found_selectors = []

        for css_selector in tqdm(generic_rules, desc='generic rules', total=len(generic_rules)):
            try:
                elements = soup.select(str(css_selector))
                if len(elements) > 0:
                    found_selectors.append(css_selector)
            except:
                print('Ignoring selector: ' + css_selector)
        ###THIS NEEDS TO BE CHECKED. CURRENTLY ASSUMES THAT ONE LINE HAS ONLY ONE SELECTOR FOR A DOMAIN
        if domain in domain_specific_rules:
            for selector in domain_specific_rules[domain]:
                elements = soup.select(str(selector))
                if len(elements) > 0:
                    found_selectors.append(selector)

        if len(found_selectors) > 0:
            text_file = open("results/banner_domain.txt", "a")
            text_file.write(domain + ',' + str(len(found_selectors)) + "\n")
            text_file.close()

        for i, selector in enumerate(found_selectors):
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                element_screenshot = element.screenshot_as_png
                #save the screenshot
                with open(os.path.join('results/screenshots/', f'{domain}-{i+1}.png'), 'wb') as f:
                    f.write(element_screenshot)

            except Exception as e:
                print('error with ' + selector.strip() + 'on domain: ' + domain + '. probably 0 width element')
                continue

    except Exception as e:
        print("There was an error accessing url:" + url)
        not_accessed = open("results/not_accessed.txt", "a")
        not_accessed.write(domain + "\n")
        not_accessed.close()
        print('Facing error: ' + str(e) + ' ' + css_selector)

text_file.close()
driver.close()