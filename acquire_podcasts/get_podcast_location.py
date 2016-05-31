# -*- coding: utf-8 -*-
"""
Created on Sat May 14 17:45:24 2016

@author: sheldon
"""

'''

#use selenium

go to so-nik.com
enter search query
click search
select first result
select link
save url to list


'''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import csv

podcastList = open('top100_1.txt').readlines()
podcastList = map(lambda x: x.strip(),podcastList)

driver = webdriver.Firefox()

def get_podcast_url(podcast_title):
    driver.get("http://itunes.so-nik.com/index.php")
    elem = driver.find_element_by_name("terms")
    elem.send_keys("%s" % podcast_title)
    elem.send_keys(Keys.RETURN)
    formatted_title = '-'.join(podcast_title.lower().split())
    try:
        driver.find_element_by_css_selector("a[href*='%s']" % formatted_title).click()
    except:
        print 'Unable to find podcast'
        return 'na'
    podcast_title_split = podcast_title.split()
    
    def find_url(string):
        try:
            print string
            link = driver.find_element_by_css_selector("a[href*='%s']" % string.lower()).text
            return link
        except:
            print 'unable to find lowercased text'
        try:
            print string
            link = driver.find_element_by_css_selector("a[href*='%s']" % string.capitalize()).text
            return link
        except:
            print 'unable to find capitalized text'

    podcastUrlList = []
    podcastUrlList.append(podcast_title)
    for i in podcast_title_split:
        podcastUrlList.append(find_url(i))
    return set(podcastUrlList)


podcast_urls = []
for i in range(0,len(podcastList)):
    podcast_url = get_podcast_url(podcastList[i])
    podcast_urls.append(podcast_url)


