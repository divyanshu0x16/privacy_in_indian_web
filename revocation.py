from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import csv
import re
import sys
import os
import time

if not os.path.exists("results"):
    os.makedirs("results")

with open('banner_domain.csv', mode='r') as file:
    csvFile = csv.reader(file)
    websites = []
    for lines in csvFile:
        websites.append('https://' + lines[0] + "/")


chrome_options = Options()
chrome_options.add_argument("--headless")

service = Service(executable_path="/home/divyanshu/Documents/Academics/Sem8/Privacy\ Considerations\ of\ the\ Indian\ Web\ Ecosystem/scraper/chromedriver")

#TODO:- Check for other closely related terms etc. Such as:- 'cookie's settings' etc.
possible_revocation = ['cookie preferences', 'cookie settings', 'consent manager', 'privacy settings', 'manage cookies']

def scraper(url):
    driver = webdriver.Chrome(options=chrome_options, service=service)
    domain = re.search(r"(?:https?://)?(?:www\.)?(.+?)/", url).group(1) #get domain name
    
    try:
        driver.set_page_load_timeout(30)
        print("Scraping URL: " + url.strip())
        driver.get(url)
        time.sleep(3)
        dom = driver.page_source

        flag = 0
        for _str in possible_revocation:
            if( _str in dom.casefold() ):
                flag = 1
                print('Found ', _str, 'in', domain)
                text_file = open("results/revocation.txt", "a")
                text_file.write(domain + ',' + str(_str) + "\n")
                text_file.close()
                break

        #POSSIBLE WAY TO SEARCH FOR COOKIE NOTICE
        #TODO:- Do this using n-grams | site, websites or services etc.
        cookie_notice = 'by continuing to use this site' # OR serves cookies to analyse traffic to this site
        if(flag == 0):
            if( cookie_notice in dom.casefold() ):
                flag = 1
                print('Found cookie notice in ', domain)
                text_file = open("results/revocation.txt", "a")
                text_file.write(domain + ',' + str('Cookie Notice') + "\n")
                text_file.close()
        
        if(flag == 0):
            text_file = open("results/revocation.txt", "a")
            text_file.write(domain + ',' + str('None') + "\n")
            text_file.close()         

    except Exception as e:
        print("There was an error accessing url:" + url)
        not_accessed = open("results/revocation.txt", "a")
        not_accessed.write(domain + ',' + str('Not accessed') + "\n")
        not_accessed.close()
        print(e)

    except KeyboardInterrupt:  
        print('Terminating Now...')  
        sys.exit(0)


for url in websites:
    scraper(url)



