'''
File            grab_station_data.py
Author          Conner Brown
Date Created    05/06/2018
Date Updated    05/06/2018
Description     Use Selenium to navigate allaccess.com for radio station data.
'''

### Example opening python.com and printing the title
'''
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome()
driver.get("http://www.python.org")
print (driver.title)
assert "Python" in driver.title
elem = driver.find_element_by_name("q")
elem.clear()
elem.send_keys("pycon")
elem.send_keys(Keys.RETURN)
assert "No results found." not in driver.page_source
driver.close()

'''
### go to allaccess.com/nielsen/markets and pull market data 
### -> go to each market link and pull station data 
### -> go to station link and pull twitter handle
import time
import csv
from selenium import webdriver

driver = webdriver.Chrome()

base_url = "http://www.allaccess.com"
markets_ext = "/nielsen/markets"
# go to market page
driver.get(base_url + markets_ext)
# log in
username = driver.find_element_by_id("username")
password = driver.find_element_by_id("password")
username.send_keys("cobrobrown")
password.send_keys("nonono1")
driver.find_element_by_name("submit").click()
driver.implicitly_wait(5)
# grab market table
market_table = driver.find_element_by_id("nielsenMarkets").find_element_by_css_selector('tbody')
# prepare csv header with market fieldnames (add station fieldnames during iteration)
fieldnames = set(['Rank','Market Name','State','Updated','Population','Black','Hispanic', 'Station URL'])
market_iter_dict = {0:'Rank',1:'Market Name',2:'State',3:'Updated',4:'Population',5:'Black',7:'Hispanic'}
row_data = []
# iterate the market_num'th market_row in market_table
market_table_tr = market_table.find_elements_by_css_selector('tr')
for market_num in range(len(market_table_tr)):
    driver.switch_to.window(driver.window_handles[0]) # switch back to main window after closing previous tab
    market_row = market_table_tr[market_num]
    market_row_data = {}
    market_url = ''
    market_id = 'arbitron-report-market-'
    market_row_num = 1
    print ("\nROW {} DETAILS\n\n".format(market_num))
    market_elements = market_row.find_elements_by_css_selector('td')
    for market_row_num in range(len(market_elements)-2):
        if market_row_num == 6:
            continue
        market_element = market_elements[market_row_num]
        market_row_data[market_iter_dict[market_row_num]] = market_element.text
        if market_row_num == 1:
            market_href = market_element.find_element_by_css_selector('a')
            print ("MARKET HREF: {}".format(market_href.get_attribute('href')))
            market_url = market_href.get_attribute('href')
            market_id += market_url.split('/')[-2] # grab market number from url
    print (len(market_row_data), market_row_data)
    # open station tab
    driver.execute_script("window.open();")
    driver.switch_to.window(driver.window_handles[1])
    driver.get(market_url)
    # get headers from station table, build station_row_data dictionary
    station_thead = driver.find_element_by_id(market_id).find_element_by_css_selector('thead').find_element_by_css_selector('tr').find_elements_by_css_selector('th')
    station_iter_dict = {}
    for station_th_num in range(len(station_thead)):
        station_iter_dict[station_th_num] = station_thead[station_th_num].text
    # update fieldnames with station_iter_dict for potentially new values
    fieldnames.update(station_iter_dict.values())
    # get data from elements in each row, write it to csv file
    station_tbody = driver.find_element_by_id(market_id).find_element_by_css_selector('tbody')
    station_num = 1
    for station_row in station_tbody.find_elements_by_css_selector('tr'):
        station_row_data = {}
        station_url = ''
        station_row_num = 1
        print ("\nSTATION {} DETAILS".format(station_num))
        station_rows = station_row.find_elements_by_css_selector('td')
        for station_row_num in range(len(station_rows)):
            station_element = station_rows[station_row_num]
            station_row_data[station_iter_dict[station_row_num]] = station_element.text
            if station_row_num == 0:
                # find the second href
                station_a = station_element.find_elements_by_css_selector('a')
                try:
                    station_url = station_a[1].get_attribute('href')
                except IndexError:
                    print ("no Station URL")
                    station_url = ''
                station_row_data['Station URL'] = station_url
        station_row_data.update(market_row_data)
        row_data.append(station_row_data)
        print (station_row_data)
        print ("STATION HREF: {}".format(station_url))
        station_num += 1
    # close tab
    driver.close()
driver.quit() # close the browser

# save data in csv
with open('station_data.csv', 'w', newline = '') as csvfile:
    wr = csv.DictWriter(csvfile, fieldnames)
    wr.writeheader()
    for row_dict in row_data:
        wr.writerow(row_dict)




