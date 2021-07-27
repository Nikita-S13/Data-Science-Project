#!/usr/bin/env python
# coding: utf-8

# In[17]:


import requests
from bs4 import BeautifulSoup
import pandas as pd
import os


# In[18]:


def get(url):
    try:
        page = requests.get(url)
        if page.status_code == 200:
            soup = BeautifulSoup(page.text, 'lxml')
            return soup
        else:
            print('failed')
    except Exception as e:
        print(e)


# In[19]:


def collect(soup,container):
    if soup:
        names = soup.find_all('div',attrs={'class':'_3wU53n'})
        prices = soup.find_all('div',attrs={'class':'_1vC4OE _2rQ-NK'})
        ratings= soup.find_all('span',attrs={'class':'_38sUEc'})
        try:
            url = soup.find_all('a',attrs={'class':'_3fVaIS'})[1]
        except:
            url = soup.find('a',attrs={'class':'_3fVaIS'})
        for nm,pr,rt in zip(names,prices,ratings):
            item = {'product':nm.text,
                    'price':pr.text,
                    'ratings':rt.text}
            container.append(item)
        if url:
            url = url.attrs.get('href')
            curl = "https://www.flipkart.com"+url
            print('next page link ==>',curl)
            return curl,container
        else:
            print('no next url found')
            return None,container
            


# In[20]:


def save(filename,datalist):
    data= pd.DataFrame(datalist)
    data.to_csv(filename)
    print('saved to',filename)
    return data


# In[21]:


container = []
url = "https://www.flipkart.com/search?q=mobiles"
while True:
    soup = get(url)
    newurl,container = collect(soup,container)
    if not newurl:
        print('the end')
        break
    else:
        url = newurl
save(filename='flipkart.csv',datalist=container)


# In[ ]:


