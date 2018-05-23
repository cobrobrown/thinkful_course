'''
File            grab_twitter_data.py
Author          Conner Brown
Date Created    05/07/2018
Date Updated    05/07/2018
Description     Use Selenium to navigate radio station sites to extract twitter handles.
'''
import time
start = time.time()
import pandas as pd
import tweepy
from tweepy.error import TweepError
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, InvalidArgumentException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

data_path = 'station_data.csv'
df = pd.read_csv(data_path)

caps = DesiredCapabilities.FIREFOX.copy()
caps["pageLoadStrategy"] = "none"
driver = webdriver.Firefox(capabilities=caps)
twitter_handles = []
station_num = 0
runtime_start = time.time()
for station_url in df['Station URL']:
    if (station_num % int(len(df.index) / 200)) == 0:
        print ("\n\n\n\n\n\n" + str(station_num) + " OUT OF " + str(len(df.index)))
        print ("RUNTIME %0.2f \n\n\n\n" % (time.time() - runtime_start))
    # go to station page
    try:
        driver.get(station_url)
    except InvalidArgumentException as e:
        twitter_handles.append([None])
        station_num += 1        
        continue    
    time.sleep(5)
    driver.switch_to.window(driver.window_handles[0])        
    twitter_links = []
    try:
        twitter_links = WebDriverWait(driver, timeout=7).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='twitter.com']")))
        twitter_href = twitter_links.get_attribute('href').split('/')[-1]
    except (TimeoutException, NoSuchElementException, WebDriverException) as e:
        print ("ERROR GETTING TWITTER LINK AT {}".format(station_url))        
        twitter_handles.append([None])
        station_num += 1
        continue
    print ("TIME {} AT SITE: {}".format(time.time() - runtime_start, station_url))
    print (twitter_href)
    twitter_handles.append([twitter_href])
    station_num += 1
driver.quit()
df['Twitter Handles'] = twitter_handles
print ("Found {} Twitter Handles!".format(df['Twitter Handles'].isnull().sum()))
### Using tweepy to retrieve user details from screen_name
# https://stackoverflow.com/questions/38859362/tweepy-multiple-user-search
# twitter api: followers_count, friends_count, listed_count, created_at, favourites_count, verified, statuses_count
# Consumer keys and access tokens, used for OAuth
consumer_key = 'some_key'
consumer_secret = 'some_secret'
access_token = 'some_token'
access_token_secret = 'some_token_secret'
# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
user_data = pd.DataFrame(columns = ['Followers Count', 'Friends Count', 'Listed Count', 'Created At', 'Favourites Count', 'Verified', 'Statuses Count'])

def no_user_data(data):
    user_dict = {}
    for col in user_data.columns:
        user_dict[col] = None
    data = data.append(user_dict, ignore_index=True)
    return data

for twitter_handle in twitter_handles:
    if (twitter_handle is None) or (not twitter_handle):
        user_data = no_user_data(user_data)
    else:
        screen_name = twitter_handle[0]
        if not screen_name:
            user_data = no_user_data(user_data)
            continue
        print ("Retrieving {}'s info".format(screen_name))
        try:
            user = api.get_user(screen_name = screen_name)
            user_data = user_data.append({'Followers Count':user.followers_count, 
                                            'Friends Count':user.friends_count, 
                                            'Listed Count':user.listed_count,
                                            'Created At':user.created_at,
                                            'Favourites Count':user.favourites_count,
                                            'Verified':user.verified,
                                            'Statuses Count':user.statuses_count
                                            }, ignore_index = True)
        except TweepError as e:
            user_data = no_user_data(user_data)
# concatenate user_data and df
df = pd.concat([df, user_data], axis=1)

df.to_csv('data.csv')
print ("RUNTIME: %0.2f seconds" % (time.time() - start))
# eof
