import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from textblob import TextBlob
import string

def remove_punctation(text):
    for char in string.punctuation:
        text = text.replace(char,'')
    return text

def get_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity

def get_sentiment_name(text):
    blob = TextBlob(text)
    polar = blob.sentiment.polarity
    if polar > 0:
        return 'positive'
    elif polar == 0:
        return 'neutral'
    else:
        return 'negative'


def get(url):
    """
    its a funtion to get the data from webpage
    """    
    page = requests.get(url) 
    if page.status_code == 200:
        htmldata = page.text
        soup = BeautifulSoup(htmldata, 'lxml')
        print('success')
        return soup
    else:
        print('error',page.status_code)

def extract(soup):
    reviews = [] # will hold the products from a page
    titles = soup.find_all('p',attrs={'class':'_2-N8zT'})
    contents= soup.find_all('div',attrs={'class':'t-ZTKy'})
    persons = soup.find_all('p', attrs={'class':'_2sc7ZR _2V5EHH'})
    product = soup.find('div', attrs={'class':'_2s4DIt _1CDdy2'})
    for t,p,a in zip(titles,contents,persons):
        data = {
            'title' : t.text,
            'content' : remove_punctation(p.text),
            'person':a.text,
            'product':product.text,
            'sentiment':get_sentiment(p.text),
            'sentiment_name':get_sentiment_name(p.text),
        }   
        reviews.append(data)
    print('total reviews collected',len(reviews))
    return reviews

def get_reviews(df, limit=10):
    dataset = []
    urls = df.link.tolist()[:limit]
    for url in urls:
        url = url.replace("/p/","/product-reviews/")
        try:
            dataset.extend(extract(get(url)))
        except Exception as e:
            print(e)
    return dataset

if __name__ == "__main__":
    df = pd.read_csv('scraped_data/product_laptop.csv')
    dataset = get_reviews(df) 