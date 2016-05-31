import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import urllib2
import re
import xmltodict
import wget
import os

os.chdir('/Users/sheldon/git/springboard_capstone/acquire_podcasts')
df = pd.read_csv('pcast.csv',names=['name','url'])
urls = df.url.tolist()
urls = filter(lambda string: 'feeds.' in string or 'feed.' in string, urls)
urls = urls[7:]

def homepage(request):
    file = urllib2.urlopen(request)
    data = file.read()
    file.close()

    def get_mp3s(data):
        data = data.split()
        data = filter(lambda word: word.endswith('.mp3"') , data)
        data = list(set(data))
        return data
    data = get_mp3s(data)  

    def parse_mp3(urlstring):
        urlstring = re.split('url=', urlstring)[1]
        return urlstring.replace('"','')
    
    data = map(parse_mp3, data)

    return data

def download_mp3(podcastseries, urls):
    os.chdir('/Users/sheldon/git/springboard_capstone/acquire_podcasts')
    os.mkdir(urls.split('/')[-1])
    os.chdir(urls.split('/')[-1])
    mp3_list = []
    def download(episode):
        print 'downloading: ',episode
        episode = wget.download(episode)
        print 'downloaded: ',episode

    for number, episode in enumerate(podcastseries):
        if len(mp3_list) < 11:
            print number, ': ', episode
            mp3_list.append(episode)
            download(episode)
            print 'length: ',len(mp3_list)
        else:
            break
    os.chdir('/Users/sheldon/git/springboard_capstone/acquire_podcasts')
    
for number, series in enumerate(urls):
    print 'starting: ',number, ' - ',series
    data = homepage(series)
    download_mp3(data, series)
    print 'completed: ',number, ' - ',series