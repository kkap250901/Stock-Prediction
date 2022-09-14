from ntpath import join
from IPython import display
import math
from pprint import pprint
import pandas as pd
import numpy as np
import nltk
import matplotlib.pyplot as plt
import seaborn as sns
import praw
import urllib.request,sys,time
import requests
from bs4 import BeautifulSoup
import requests
import json
from Supplementary_fns import get_date
from Supplementary_fns import indataframe
from Supplementary_fns import merging


# Instansiating an instance of the Reddit class
reddit = praw.Reddit(client_id = '7hJXdlOQrZBe5CLnz-6Iow',
                client_secret = '9OfUiQtg9wJOlta1hJooEcgUTatMkA',
                user_agent = 'DragonflyOk1283'
            )


#its bad practice to place your bearer token directly into the script (this is just done for illustration purposes)
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAECKgQEAAAAA9d7wW%2FntXqlEqIhO3Zb%2FmYEsQR8%3DgYRJHrno8YqhEtBzTA3ZsSvLt8Vq5Qf3MBCTnZCkSg2MysCDGM"


# Getting Reliance Up to date macroeconomic data 
def macrodata():
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=RELIANCE.BSE&outputsize=full&apikey=DZAAS8KBFW1H69LE'
    r = requests.get(url)
    data = r.json()
    df = pd.DataFrame.from_dict(data['Time Series (Daily)'],orient='index')
    df.columns = ['Open','High','Low','Close','Volume']
    df.index.names = ['Date']
    df = df.reset_index()
    df.Date = pd.to_datetime(df.Date)
    df = df[df['Date'] < '2022-09-10']
    df.Date = df.Date.astype('str')
    return df


# Getting Gold data for the past year
def golddata(latest_date):
    base_currency = 'XAU'
    symbol = 'INR' 
    endpoint = 'timeseries'
    start_date = '2021-09-09'
    end_date = latest_date
    access_key = 'ind54w6v11p4vll9bdyl35mk6ad5817upr5o7gkpf2fuyu6q6w999suifx34'

    resp = requests.get(
        'https://www.commodities-api.com/api/'+endpoint+'?access_key='+access_key+'&start_date='+start_date+'&end_date='+end_date+'&base='+base_currency+'&symbols='+symbol)
    # if resp.status_code != 200:
    #     # This means something went wrong.
    #     raise ('GET /'+endpoint+'/ {}'.format(resp.status_code))
    d = resp.json()
    dfgold = pd.DataFrame.from_dict(d['data']['rates'],orient='index')
    dfgold.index.name = 'Date'
    dfgold = dfgold.reset_index()
    return dfgold


# Getting oil data for the last year 
def oildata(latest_date):
    base_currency = 'BRENTOIL'
    symbol = 'INR' 
    endpoint = 'timeseries'
    start_date = '2021-09-09'
    end_date = latest_date
    access_key = 'ind54w6v11p4vll9bdyl35mk6ad5817upr5o7gkpf2fuyu6q6w999suifx34'
    resp = requests.get(
        'https://www.commodities-api.com/api/'+endpoint+'?access_key='+access_key+'&start_date='+start_date+'&end_date='+end_date+'&base='+base_currency+'&symbols='+symbol)
    d = resp.json()
    dfoil = pd.DataFrame.from_dict(d['data']['rates'],orient='index')
    dfoil.index.name = 'Date'
    dfoil = dfoil.reset_index()
    return dfoil


# Get the USD-INR Exchange rate from the last year
def exchangedata(latest_date):
    url = f"https://api.apilayer.com/exchangerates_data/timeseries?start_date=2021-09-10&end_date={latest_date}&base=USD&symbols=INR"
    payload = {}
    headers= {"apikey": "ZtkAIYrfLdUk9p58uEkeIwJV1uWAdP8u"}
    response = requests.request("GET", url, headers=headers, data = payload)
    status_code = response.status_code
    if status_code !=200:
        print(f'status_code : {status_code}')
    result = response.json()
    dfexchange = pd.DataFrame.from_dict(result['rates'],orient='index')
    dfexchange.index.name = 'Date'
    dfexchange = dfexchange.reset_index()
    return dfexchange


# Getting the different reddit data 
def redditpolitics():
    allpolitics = []
    allheadlines = []
    date1 = []
    date2 = []

    # This is for the political news 
    for submission in reddit.subreddit('politics').top(time_filter="year",limit=None):
        allpolitics.append(submission.title)
        date = get_date(submission)
        date1.append(date)
        
    # This is for the indian news with specific political and Buiness news
    for submission in reddit.subreddit('india').search('flair:Policy/Economy OR flair:Business/Finance OR flair:Politics OR flair:Science/Technology',time_filter='year',limit=None):
        allheadlines.append(submission.title)
        date = get_date(submission)
        date2.append(date)
        
    politics = {'Date':date1,'Politics':allpolitics}
    news_headlines = {'Date':date2,'Headlines':allheadlines}
    politicsdf = pd.DataFrame.from_dict(politics)
    news_headlinesdf = pd.DataFrame.from_dict(news_headlines)
    return politicsdf,news_headlinesdf


#  All Financial Time articles 
def ftnews():
    news_titles=[]
    dates = []
    for page in range(1,20):
        url="https://www.ft.com/india?page={}".format(page)
        result=requests.get(url)
        reshult=result.content
        reshult2 = result.text
        soup=BeautifulSoup(reshult, "html.parser")
        for title in soup.findAll("div",{"class":"o-teaser__heading"}):
            titles=title.find(text=True)
            if titles == 'Follow us on Twitter @FTIndianews':
                break
            news_titles.append(titles)
        for date in soup.findAll("div",{"class":'stream-card__date'}):
            date = date.find('time').get('datetime').strip()
            dates.append(date)

    if len(news_titles) == len(dates):
        dictionary = {'Date':list(dates),'News_titles':list(news_titles)}

    ftdf = pd.DataFrame.from_dict(dictionary)
    return ftdf
    

#define search twitter function
def search_twitter(query, tweet_fields,max_results, bearer_token = BEARER_TOKEN):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}

    url = "https://api.twitter.com/2/tweets/search/recent?query={}&{}&{}".format(
        query, tweet_fields,max_results
    )
    response = requests.request("GET", url, headers=headers)

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

# 
def gettweets(query = "-is%3Aretweet Reliance Industries Limited"):
    toptweets  = list()
    dates = list()
    #search term

    #twitter fields to be returned by api call
    tweet_fields = "tweet.fields=created_at"
    max_results = f'max_results={100}'

    #twitter api call
    json_response = search_twitter(query=query, tweet_fields=tweet_fields,max_results=max_results, bearer_token=BEARER_TOKEN)
    #pretty printing
    # print(json.dumps(json_response, indent=4, sort_keys=True))

    for dict in json_response['data']:
        toptweets.append(dict['text'])
        dates.append(dict['created_at'])
    
    dictionary = {'Date' : dates,'Tweets':toptweets}
    twitterdf = pd.DataFrame.from_dict(dictionary)
    return twitterdf


def everything():  
    #Getting Macro data
    reliance = macrodata()
    #Getting Gold data
    gold = golddata(latest_date=reliance.Date.max())
    #Getting oil price data
    oil = oildata(latest_date=reliance.Date.max())
    #Getting the exchange rate data
    exchange = exchangedata(latest_date=reliance.Date.max())
    #merging on the date for the overall macro dataset
    macro = pd.merge(pd.merge(reliance,oil,on='Date',how='inner'),
            (pd.merge(gold,exchange,on='Date',how='inner')),on='Date',how='inner')
    # Getting reddit data in dictionaries
    allpolitics,headlines = redditpolitics()
    # Getting ft news in dictionary
    ftarticles = ftnews()
    # Getting alltweets related to reliance
    reliancetweets = gettweets()
    # Making into datframe
    allsentiments = [allpolitics,headlines,ftarticles,reliancetweets]
    # Converting them all into dataframes and returning a list of those dataframes
    sentimentdf = merging(allsentiments)
    # Return the dataframe
    return sentimentdf,macro


# Running all the functions to get all the data
if __name__ == '__main__':
    sentiment,macro = everything()
    sentiment.to_excel('allarticles.xlsx')
    macro.to_excel('Stock-data.xlsx')


