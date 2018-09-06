#!/usr/bin/env python3

import re
import os
import sys
configfile = "{0}/repo/projects/utils/".format(os.path.expanduser('~'))
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
import my_utils as my
import time
from selenium import webdriver
from selenium.webdriver.common import action_chains, keys

user = ""
pwd = ""
with open("{0}/password".format(os.path.expanduser('~')), 'r') as f:
    user = f.readline().rstrip('\n')
    pwd = f.readline().rstrip('\n')

stock_list = "{0}/repo/projects/stocks/data/sp100_stocks.txt".format(os.path.expanduser('~')) 

driver = webdriver.Chrome()
driver.get("https://www.fidelity.com/login/accountposition?AuthRedUrl=https://oltx.fidelity.com/ftgw/fbc/ofsummary/defaultPage&AuthOrigUrl=https://scs.fidelity.com/customeronly/accountposition.shtml")
action = action_chains.ActionChains(driver)

time.sleep(2)
elem = driver.find_element_by_id("userId-input")
elem.send_keys(user + keys.Keys.TAB)
elem = driver.find_element_by_id("password")
elem.send_keys(pwd + keys.Keys.TAB)
elem = driver.find_element_by_id("fs-login-button").click()

time.sleep(5)
option_page = "https://researchtools.fidelity.com/ftgw/mloptions/goto/optionChain?symbols="

with open(stock_list, 'r') as f:
    next(f)
    for line in f:
        symbol = line.strip().split(',')[0]
        
        driver.get("{0}{1}".format(option_page, symbol))
        innerHTML = driver.execute_script("return document.body.innerHTML")
        soup = my.get_soup_str(innerHTML)
        price = "No Options"
        for number in soup.find_all("span", {"class" : "main-number"}):
            price = number.string[1:].replace(',','')
    
        print("{0} : {1}".format(symbol, price))

        for table in soup.find_all("div", {"class" : "symbol-results-data-table"}):
            for header in table.find_all("thead", {"class" : "js-lock-target"}):
                '''
                    Because there is a class = "js-lock-target clone" which the header results
                    to a list as ["js-lock-target", "clone"]
                '''
                #if len(header['class']) == 1:
                #    for rows in header.find_all("th"): 
                #        if rows.has_attr('name'):
                #            print(rows['name'])
            strike_date = ""
            days_to_expiry_regex = "(.+)\(([0-9]+)\s+.+"
            days_to_expiry = ""
            ask = 0.0
            strike = 0.0
            count = 0
            for body in table.find_all("tbody"):
                for row in body.find_all("tr"):
                    m = re.match(days_to_expiry_regex, row['id'])
                    if m:
                        days_to_expiry = int(m.group(2))
                        expiry = m.group(1)
                    else:
                        count += 1
                        for data in row.find_all("td"):
                            if data.has_attr("name"):
                                if data["name"] == "Ask Calls":
                                    ask = float(data.string)
                                if data["name"] == "Strike":
                                    strike = float(data.string.replace(',',''))
                        
                        if count == 5:
                            print("{},{},{},{}".format(symbol,strike,expiry,(ask+strike)/float(price) - 1))
                        elif count == 10:
                            count = 0                 
driver.close()
