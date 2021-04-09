# -*- coding: utf-8 -*-
"""
Created on Sun Oct 11 17:01:47 2020

@author: Vinson Phoan
"""

from selenium import webdriver
import time
import re
import pandas as pd 
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import string
from nltk.tokenize import word_tokenize 
import nltk
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory, StopWordRemover, ArrayDictionary
import numpy as np
from textblob import TextBlob
from matplotlib import pyplot as plt

class Twitter():
    
    #target link twitter yang sudah search, pastikan yang latest
    #year_now tahun ini tahun berapa, contoh 2020
    def __init__(self, target):
        self.target = target
        self.raw_tweets = [] #data pertama kali di ambil
        self.separated_tweets = [] #misahkan text
        
    def get_chrome_driver(self, driver):
        self.driver = webdriver.Chrome(driver)
        
    def connect(self):
        self.driver.get(self.target)
        time.sleep(5)
        
    def scrape(self, pages):
        #pages itu total halaman
        for i in range(0,pages):
            tweet_scrap = self.driver.find_element_by_xpath("//*[@id='react-root']/div/div/div[2]/main")
            self.raw_tweets.append(tweet_scrap.text)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
    
    #cari tanggal yang benar dari tweet
    def find_date(self,tweet):
        months = ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
        r = re.compile('[a-zA-z]{3} \d+') # yang tidak ada tahun 
        r2x = re.compile('[a-zA-z]{3} \d+,\W\d+') #regex yang ada tahun
        month_tweet = r.findall(tweet)
        month_tweet2 = r2x.findall(tweet)
        month_tweet_org = []
        choose_auto_month = []
        if len(month_tweet2) == 0:
            choose_auto_month = month_tweet
        else:
            choose_auto_month = month_tweet2
            
        for i  in choose_auto_month:
            check = i[:3].lower() in months
            if check:
                month_tweet_org.append(i)
        return month_tweet_org
        
        
    #misahkan text,username,dll dan diambil cuma date dan tweet
    def separate_tweets(self):
        self.separated_tweets.clear()
        for tw in self.raw_tweets:
            tweet_date = self.find_date(tw)
        
            tw_splitting = tw.split("@")
            for i in range(len(tw_splitting)):
                a =  tw_splitting[i].split("\n")
                for j in range(len(a)):
                    if a[j] in tweet_date:
                        self.separated_tweets.append([a[j],a[j+1]])
                        
        return self.separated_tweets
                
            
    
    
    def check_raw_tweets(self):
        return self.raw_tweets

    


    def removeDuplicate(self,data): 
            #hapus tweets yang sama
            duplicateList = [] 
              
            for x in data: 
                if x not in duplicateList: 
                    duplicateList.append(x)
            return duplicateList
    
    def removeSpecificList(self,data, target):
        #target bearti list yang akan di hapus jika mengandung target tersebut
        removedTargetData = []
        for i in data:
            
            if str(i[1]).lower().strip() not in target:
                removedTargetData.append(i)
    
        return removedTargetData


        

if __name__ == '__main__':
    
    #bagian scraping data
    url = "https://twitter.com/search?q=saham%20bank%20danamon&src=typed_query&f=live"
    twitter = Twitter(url)
    twitter.get_chrome_driver('C:\chromedriver')
    twitter.connect()
    twitter.scrape(100)
    checkdata = twitter.check_raw_tweets()
    check = twitter.separate_tweets()
    list_unused_word = [" ","","replying to","[camtion]",'-']
  
    check2 = twitter.removeSpecificList(check,list_unused_word)   #hapus data yang duplikat dan list yang ada replying to,dll
    check2 = twitter.removeDuplicate(check2)

    
    #save data ke csv
    df = pd.DataFrame(check2)
    df.to_csv('sentimentdanamon.csv', index=False)
    
    
    
    
    #MULAI DARI SINI
    #import dataset
    data = pd.read_csv("sentimentdanamon.csv")
    data=data.astype(str)
   
 
    tanggal = data.iloc[:,0].values
    tweet = data.iloc[:,1].values
    
    
    #data preprocessing /  Cleaning data

    
    #Case folding

    tweet = [re.sub(r"(?:@\S*|#\S*|http(?=.*://)\S*)", "", i).strip() for i in tweet] # hapus url dan hastag
    
    #ubah ke lowercase
    tweet =[x.lower() for x in tweet]
    
    #hapus angka
    tweet = [re.sub(r"\d+", "", x) for x in tweet]
    
    #Hapus simbol
    tweet = [x.translate(str.maketrans("","",string.punctuation)) for x in tweet]
    
    #hapus whitespace
    tweet = [x.strip() for x in tweet]
    
        
    
    #STEMMING
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    hasilStem = [stemmer.stem(x) for x in tweet]

    
    #TOKENIZING
    #pisahkan setiap kata 
    #nltk.downloads()
  
   # factory = StopWordRemoverFactory()
   # stopwords = factory.get_stop_words()
    
    stop_factory = StopWordRemoverFactory().get_stop_words()
    more_stopword = ['yg', 'online']#tambahan stop words
    stopwords = stop_factory + more_stopword
    dictionary = ArrayDictionary(stopwords)
    rem = StopWordRemover(dictionary)
    tokens = [word_tokenize(rem.remove(x)) for x in hasilStem]

  
    #Gabungkan kata menjadi kalimat dan tabel kembali
    cleanedData = [''.join(x) for x in hasilStem]
    
    data2= np.stack((tanggal, cleanedData),axis = 1)
    data3 = pd.DataFrame(data2,columns=['tanggal', 
                  'tweets'])
    

    
    def getPola(text):
        return TextBlob(text).sentiment.polarity
    
    data3['Polarity'] = data3['tweets'].apply(getPola)
    
    data3['Polarity'] = aa


    
    def getScore(score):
        if(score<0):
            return "Negative"
        elif(score==0):
            return "Neutral"
        else:
            return "Positive"
    data3["Score"] = data3['Polarity'].apply(getScore)
        
    
    def getScore1score(score):
       a= 0
       b= 0
       c=0
       for i in score:
           if(i<0):
               a +=1
           elif(i==0):
               b +=1
           else:
              c+=1
       print(a)
       print(b)
       print(c)
    
        

    plt.figure(figsize=(8,6))
    for i in range(0, data3.shape[0]):
        plt.scatter(data3['Polarity'][i],data3['Subjectivity'][i],color='blue')
        
    plt.title("Sentiment Analysis")
    plt.xlabel("Polarity")
    plt.ylabel("Subjectivity")
    plt.show()
    
    
    countpos = len([i for i in data3['Score'] if i == "Positive"])
    countpos = round(countpos/data3.shape[0]*100,1)


    plt.hist(data3['Score'])
    plt.title("Sentiment Analysis Bank Danamon 2012-2020")
    plt.ylabel("Number of tweets")
    plt.show()
    
   # data3.to_csv('hasilSentimenAnalysis.csv', index=True)
    




    





    
    
    