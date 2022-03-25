import time
import_start_time = time.time()
import tweepy
import pandas as pd
import pythainlp
from pythainlp.corpus import thai_stopwords
from pythainlp.util import normalize
import nltk
from nltk.corpus import stopwords
import re
import matplotlib
import matplotlib.pyplot as plt
import emoji
import datetime
import os
from timestamp import Timestamp
import threading
from geopy.geocoders import Nominatim
import random
from sentiment import Sentiment
from textblob import TextBlob
import folium
import_stop_time = time.time()
print(f"import time : {import_stop_time-import_start_time}")

class TwitterAPI(object):

    # Setup API
    def __init__(self,lang="en"):
        self.api_key = "MY_API_KEY"
        self.api_key_secret = "MY_API_KEY_SECRET"
        self.access_token = "MY_ACCESS_TOKEN"
        self.access_token_secret = "MY_ACCESS_TOKEN_SECRET"
        self.auth = tweepy.OAuthHandler(self.api_key, self.api_key_secret)
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(self.auth)
        self.lang = lang
        self.th_word = set(thai_stopwords())
        self.en_word = set(stopwords.words("english"))
        self.wd_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.path = {
                    "trend" : f"{self.wd_path}\\src\\twitter\\trend",
                    "search" : f"{self.wd_path}\\src\\twitter\\search",
                    "location" : f"{self.wd_path}\\src\\twitter\\location"
                    }
        self.time = Timestamp()
        self.sent = Sentiment()
        self.map = folium.Map(location=[0, 0], zoom_start=1, tiles='Stamen Terrain')
        self.location_data = list()

    def ch_lang(self,lang):
        self.lang = lang
        print(self.lang)

    # Find Trendy Hashtag From WOEID (Where on Earth IDentifier)
    def save_trend(self):
        woeid_dict = {"en":2352824, "th":23424960}
        trendy = self.api.trends_place(woeid_dict[self.lang])
        trends = trendy[0]["trends"]
        header = list()
        trend_data = list()
        fdate = self.time.format_date()
        firsttime = True
        for trend in trends:
            keys = trend.keys()
            keys_size = len(trend.keys())
            single_trend_data = dict()
            for k in keys:
                single_trend_data[k] = trend[k]
                if firsttime:
                    header.append(k)
                    if len(header)==keys_size:
                        firsttime = False
            trend_data.append(single_trend_data)
        
        # Implement to DataFrame
        trend_df = pd.DataFrame(trend_data, columns=header)
        addr = self.path["trend"]
        trend_df.to_csv(f"{addr}\\{self.lang}\\{fdate}.csv", encoding="UTF-8")
    
    def show_trend(self, fdate="now"):
        """
        Open trends at input date.
        If now found, open the latest trends.
        """
        if fdate == "now":
            fdate = self.time.format_date()
        addr = self.path["trend"]
        try:
            f = open(f"{addr}\\{self.lang}\\{fdate}.csv","r",encoding="UTF-8")
            f.close()
        except FileNotFoundError:
            try:
                fdate = self.time.format_date()
                f = open(f"{addr}\\{self.lang}\\{fdate}.csv","r",encoding="UTF-8")
                f.close()
            except FileNotFoundError:
                self.save_trend()

        trend_data = pd.read_csv(f"{addr}\\{self.lang}\\{fdate}.csv",encoding="UTF-8")
        trend_name = list(trend_data["name"])

        out = list()
        for trend in trend_name:
            out.append(trend)

        return out

    # Search
    def search(self, key, date="now"):
        """
        Search through TwitterAPI with query and until parameter.
        Only collect original tweet(Not Retweet status).
        Get author, language, retweet count, time, text of each tweet.
        Save it to .csv file at keyword folder as YYYYMMDD format filename.
        """
        print(f"Now do : self.search({key}, {date})")
        if date == "now":
            date = self.time.get_date_now()
        fdate = self.time.format_date(date)
        status_data = list()
        # EN
        en_result = tweepy.Cursor(self.api.search, 
                                q=key, lang="en", 
                                result="recent", 
                                include_entities=False,
                                since=datetime.date.fromisoformat(date) - datetime.timedelta(days=1),  
                                until=date).items(50)
        # Get status text. If retweeted, delete @RT        
        for en_tweet in en_result:
            if hasattr(en_tweet, "retweeted_status"):
                try:
                    text = en_tweet.retweeted_status.extended_tweet["full_text"]
                except AttributeError:
                    text = en_tweet.retweeted_status.text
            else:
                try:
                    text = en_tweet.extended_tweet["full_text"]
                except AttributeError:
                    text = en_tweet.text

            cleaned_text = self.texttool(text)
            # location
            if len(en_tweet.user.location) > 0:
                location = en_tweet.user.location
            else:
                location = ""
            single_tweet_data = {"author" : en_tweet.author.screen_name,
                                "location" : location,
                                "language" :  en_tweet.lang,
                                "retweet" : en_tweet.retweet_count,
                                "time" : en_tweet.created_at,
                                "text" : cleaned_text}
            status_data.append(single_tweet_data)

        # TH 
        th_result = tweepy.Cursor(self.api.search, 
                                q=key, lang="th", 
                                result="recent", 
                                include_entities=False,
                                since=datetime.date.fromisoformat(date) - datetime.timedelta(days=1),  
                                until=date).items(50)
        for th_tweet in th_result:
            if hasattr(th_tweet, "retweeted_status"):
                try:
                    text = th_tweet.retweeted_status.extended_tweet["full_text"]
                except AttributeError:
                    text = th_tweet.retweeted_status.text
            else:
                try:
                    text = th_tweet.extended_tweet["full_text"]
                except AttributeError:
                    text = th_tweet.text

            cleaned_text = self.texttool(text)
            # location
            if len(th_tweet.user.location) > 0:
                location = th_tweet.user.location
            else:
                location = ""
            single_tweet_data = {"author" : th_tweet.author.screen_name,
                                "location" : location,
                                "language" :  th_tweet.lang,
                                "retweet" : th_tweet.retweet_count,
                                "time" : th_tweet.created_at,
                                "text" : cleaned_text}
            status_data.append(single_tweet_data)
        
        # Dir making
        addr = self.path["search"]
        search_df = pd.DataFrame(status_data, columns=["author", "location", "language", "retweet", "time", "text"])
        search_df = search_df.drop_duplicates(subset="text")
        search_df.to_csv(f"{addr}\\{key}\\{fdate}\\result.csv",encoding="UTF-8")
        print(f"Complete : self.search({key}, {date})")

    def get_searchs(self, key, start, stop):
        print(f"Now do : get_searchs({key}, {start}, {stop})")
        dates = self.time.timerange(start, stop)
        fstart = self.time.format_date(start)
        fstop = self.time.format_date(stop)
        addr = self.path["search"]
        if not(os.path.exists(f"{addr}\\{key}\\range\\{fstart}_{fstop}\\result.csv")):
            print("1")
            status_data = list()
            for date in dates:
                fdate = self.time.format_date(date)
                # open csv
                status_df = pd.read_csv(f"{addr}\\{key}\\{fdate}\\result.csv", index_col=False, encoding="UTF-8")
                author_list = list(status_df["author"])
                lang_list = list(status_df["language"])
                rt_list = list(status_df["retweet"])
                location_list = list(status_df["location"])
                time_list = list(status_df["time"])
                text_list = list(status_df["text"])
                
                for i in range(len(author_list)):
                    single_status_data = {
                                        "author" : author_list[i],
                                        "language" : lang_list[i],
                                        "retweet" : rt_list[i],
                                        "location" : location_list[i],
                                        "time" : time_list[i],
                                        "text" : text_list[i]
                                        }
                    status_data.append(single_status_data)
                    self.status_text.append(text_list[i])
            # Make DataFrame
            status_df = pd.DataFrame(status_data, columns=["author", "language", "retweet", "location", "time", "text"])
            status_df = status_df.drop_duplicates(subset="text")
            status_df.to_csv(f"{addr}\\{key}\\range\\{fstart}_{fstop}\\result.csv", encoding="UTF-8")

        else:
            print("dont have")
            status_df = pd.read_csv(f"{addr}\\{key}\\range\\{fstart}_{fstop}\\result.csv", index_col=False, encoding="UTF-8")
            text_list = list(status_df["text"])
            for text in text_list:
                self.status_text.append(text)
        print(f"Complete : get_searchs({key}, {start}, {stop})")
    
    def get_mostwords(self, key, start, stop):
        print(f"Now do : get_mostwords({key}, {start}, {stop})")
        dates = self.time.timerange(start, stop)
        fstart = self.time.format_date(start)
        fstop = self.time.format_date(stop)
        addr = self.path["search"]
        if not(os.path.exists(f"{addr}\\{key}\\range\\{fstart}_{fstop}\\chart.csv")):
            word_frequency = dict()
            word_data = list()
            for date in dates:
                fdate = self.time.format_date(date)
                # Mostword
                mw_df = pd.read_csv(f"{addr}\\{key}\\{fdate}\\chart.csv", index_col=False, encoding="UTF-8")
                word_list = list(mw_df["word"])
                freq_list = list(mw_df["volume"])
                
                for i in range(len(word_list)):
                    if word_list[i] in word_frequency:
                        word_frequency[word_list[i]] += freq_list[i]
                    else:
                        word_frequency[word_list[i]] = freq_list[i]
            
            # Make DataFrame
            # chart_label = list()
            # chart_size = list()
            # bar_count = 0
            self.mkchart_range(key, word_frequency, start, stop)
            for k, v in word_frequency.items():
                word_data.append({"word" : k, "volume" : v})
                # if bar_count < 3:
                #     chart_label.append(k)
                #     chart_size.append(v)
                #     bar_count += 1
            
            mws_df = pd.DataFrame(word_data, columns=["word", "volume"])
            mws_df.to_csv(f"{addr}\\{key}\\range\\{fstart}_{fstop}\\mostword.csv", encoding="UTF-8")
            # Matplotlib
            # matplotlib.rc("font", family="TH Sarabun New")
            # # fig, ax = plt.subplots()
            # plt.bar(chart_label, chart_size)
            # plt.title(f"{key}")
            # plt.savefig(f"{addr}\\{key}\\range\\{fstart}_{fstop}\\mostword_chart.png")
            # plt.clf()
        print(f"Complete : get_mostwords({key}, {start}, {stop})")
        
    def get_sentiments(self, key, start, stop):
        print(f"Now do : get_sentiments({key}, {start}, {stop})")
        dates = self.time.timerange(start, stop)
        fstart = self.time.format_date(start)
        fstop = self.time.format_date(stop)
        addr = self.path["search"]
        if not(os.path.exists(f"{addr}\\{key}\\range\\{fstart}_{fstop}\\sentiment.csv")):
            tag_frequency = {"pos" : 0,
                        "neg" : 0,
                        "neu" : 0}
            tag_list = list()
            for date in dates:
                fdate = self.time.format_date(date)
                # Sentiment analysis
                tag_df = pd.read_csv(f"{addr}\\{key}\\{fdate}\\sentiment.csv", index_col=False, encoding="UTF-8")
                freq_list = list(tag_df["volume"])
                tag_frequency["pos"] += freq_list[0]
                tag_frequency["neg"] += freq_list[1]
                tag_frequency["neu"] += freq_list[2]

            # Make DataFrame
            # pie_label = list()
            # pie_size = list()
            self.mkpie_range(key, tag_frequency, start, stop)
            for k, v in tag_frequency.items():
                tag_list.append({"tag" : k, "volume" : v})
            #     pie_label.append(k)
            #     pie_size.append(v)
            
            tags_df = pd.DataFrame(tag_list, columns=["tag", "volume"])
            tags_df.to_csv(f"{addr}\\{key}\\range\\{fstart}_{fstop}\\sentiment.csv")

            # # Sentiment Analysis
            # fig, ax = plt.subplots()
            # ax.pie(pie_size, labels=pie_label, startangle=90)
            # ax.axis("equal")
            # plt.title(f"{key}")
            # plt.savefig(f"{addr}\\{key}\\range\\{fstart}_{fstop}\\sentiment.png")
            # plt.clf()
        print(f"Complete : get_sentiments({key}, {start}, {stop})")

    def get_locations(self, key, start, stop):
        print(f"Now do : get_locations({key}, {start}, {stop})")
        dates = self.time.timerange(start, stop)
        fstart = self.time.format_date(start)
        fstop = self.time.format_date(stop)
        addr = self.path["search"]
        if not(os.path.exists(f"{addr}\\{key}\\range\\{fstart}_{fstop}\\location.csv")):
            location_frequency = list()
            temp_location = list()
            for date in dates:
                fdate = Timestamp().format_date(date)
                # Location data
                location_df = pd.read_csv(f"{addr}\\{key}\\{fdate}\\location.csv", index_col=False, encoding="UTF-8")
                name_list = list(location_df["location"])
                lat_list = list(location_df["latitude"])
                long_list = list(location_df["longitude"])
                count_list = list(location_df["count"])

                for i in range(len(name_list)):
                    if name_list[i] in temp_location:
                        index = temp_location.index(name_list[i])
                        location_frequency[index]["count"] += count_list[i]
                    else:
                        single_location_data = {"location" : name_list[i],
                                                "latitude" : lat_list[i],
                                                "longitude" : long_list[i],
                                                "count" : count_list[i]}
                        temp_location.append(name_list[i])
                        location_frequency.append(single_location_data)
            
            # Make DataFrame
            lo_df = pd.DataFrame(location_frequency, columns=["location", "latitude", "longitude", "count"])
            lo_df.to_csv(f"{addr}\\{key}\\range\\{fstart}_{fstop}\\location.csv")
            name_list = list(lo_df["location"])
            lat_list = list(lo_df["latitude"])
            long_list = list(lo_df["longitude"])
            count_list = list(lo_df["count"])
        else:
            # DataFrame
            location_df = pd.read_csv(f"{addr}\\{key}\\range\\{fstart}_{fstop}\\location.csv", index_col=False, encoding="UTF-8")
            name_list = list(location_df["location"])
            lat_list = list(location_df["latitude"])
            long_list = list(location_df["longitude"])
            count_list = list(location_df["count"])
            
        # Folium map
        m = folium.Map(location=[0, 0], zoom_start=1, tiles='Stamen Terrain')
        # make Marker
        for i in range(len(name_list)):
            count = int(count_list[i])
            if count <= 5:
                color = "green"
            elif count <= 10:
                color = "orange"
            else:
                color = "red"
            marker = folium.Marker(location=[lat_list[i], long_list[i]], 
                                    popup=f"<b>{name_list[i]}</b>",
                                    icon=folium.Icon(color=color, icon="info-sign"))
            marker.add_to(m)
        self.map = m
        print(f"Complete  : get_locations({key}, {start}, {stop})")

    # Mostword : single
    def mostword(self, key, fdate):
        print(f"Now do : mostword({key}, {fdate})")
        """
        Read search result file from self.search().
        Tokenize each text and make a word counter.
        Make bar chart from word counter.
        """
        addr = self.path["search"]
        status_data = pd.read_csv(f"{addr}\\{key}\\{fdate}\\result.csv",encoding="UTF-8")

        mostword = dict()
        tweet_text = list(status_data["text"])
        for i in range(len(tweet_text)):
            line = self.texttool(tweet_text[i])
            notag = self.clean_tag(line)
            # Tokenization
            first_tokenized = pythainlp.tokenize.word_tokenize(line, engine="newmm", keep_whitespace=False)
            last_tokenized = list()
            for word in first_tokenized:
                if len(word) > 1:
                    if word.lower() != key.lower():
                        if pythainlp.util.isthai(word):
                            correct = normalize(word)
                            if not(correct.lower() in self.th_word):
                                last_tokenized.append(correct)
                        else:
                            second_tokenized = nltk.word_tokenize(word)
                            for item in second_tokenized:
                                if not(item in self.en_word):
                                    last_tokenized.append(item)
            for item in last_tokenized:
                if item in mostword:
                    mostword[item] += 1
                else:
                    mostword[item] = 1

        mostword = dict(sorted(mostword.items(), key=lambda item: item[1], reverse=True))
        chart_df = pd.DataFrame(columns=["word", "volume"])

        # Word Counter
        for k, v in mostword.items():
            single_dict = {"word" : k, "volume" : v}
            chart_df = chart_df.append(single_dict, ignore_index=True)

        chart_df.to_csv(f"{addr}\\{key}\\{fdate}\\chart.csv",encoding="UTF-8")
        # Make Bar Chart
        self.mkchart(key, mostword, fdate)
        print(f"Complete : mostword({key}, {fdate})")

    # Sentiment : single
    def sentiment(self, key, fdate):
        print(f"Now do : sentiment({key}, {fdate})")
        """
        Sentiment Analysis
        """
        addr = self.path["search"]
        search_df = pd.read_csv(f"{addr}\\{key}\\{fdate}\\result.csv", index_col=False, encoding="UTF-8")
        texts = list(search_df["text"])

        # Add tag to dict
        sentiment_tweet = {"pos" : 0, "neg" : 0, "neu" : 0}
        for text in texts:
        # Sentiment
            if pythainlp.util.isthai(text):
                tag = self.sent.classify(text)
                sentiment_tweet[tag] += 1
            else:
                tag = TextBlob(text).sentiment.polarity
                if tag > 0:
                    sentiment_tweet["pos"] += 1
                elif tag < 0:
                    sentiment_tweet["neg"] += 1
                else:
                    sentiment_tweet["neu"] += 1
        
        # Turn into DataFrame
        tag_data = list()
        for k, v in sentiment_tweet.items():
            tag_data.append({"tag" : k, "volume" : v})

        sentiment_df = pd.DataFrame(tag_data, columns=["tag", "volume"])

        addr = self.path["search"]
        sentiment_df.to_csv(f"{addr}\\{key}\\{fdate}\\sentiment.csv")

        # make pie chart
        self.mkpie(key, sentiment_tweet, fdate)
        print(f"Complete : sentiment({key}, {fdate})")

    def firstsearch(self, key, dates):
        # Search func
        # Create Threads
        thread_list = list()
        for date in dates:
            t = threading.Thread(target=self.thread_search, args=(key, date))
            thread_list.append(t)
        
        # lock Threads
        # Threads start
        lock = threading.Lock()
        lock.acquire()
        for thread in thread_list:
            thread.start()
            time.sleep(0.1)
        lock.release()
        # Threads stop
        for thread in thread_list:
            thread.join()

        # Mostword, sentiment, location
        # Create Threads
        thread_list = list()
        for date in dates:
            fdate = self.time.format_date(date)

            # Mostword
            mw_t = threading.Thread(target=self.mostword, args=(key, fdate))
            # Sentiment
            s_t = threading.Thread(target=self.sentiment, args=(key, fdate))
            # Location
            lo_t = threading.Thread(target=self.location, args=(key, fdate))

            thread_list.append(mw_t)
            thread_list.append(s_t)
            thread_list.append(lo_t)
        
        # lock threads
        lock.acquire()
        for thread in thread_list:
            thread.start()
            time.sleep(0.1)
        
        lock.release()
        # Threads stop
        for thread in thread_list:
            thread.join()

    def range_func(self, key, start, stop):
        # make dir
        fstart = self.time.format_date(start)
        fstop = self.time.format_date(stop)
        addr = self.path["search"]
        if not(os.path.exists(f"{addr}\\{key}\\range\\{fstart}_{fstop}")):
            os.mkdir(f"{addr}\\{key}\\range\\{fstart}_{fstop}")
        self.status_text = list()
        thread_list = list()
        
        # Create Threads
        status_thread = threading.Thread(target=self.get_searchs, args=(key, start, stop))
        mw_thread = threading.Thread(target=self.get_mostwords, args=(key, start, stop))
        sent_thread = threading.Thread(target=self.get_sentiments, args=(key, start, stop))
        loca_thread = threading.Thread(target=self.get_locations, args=(key, start, stop))

        thread_list.append(status_thread)
        thread_list.append(mw_thread)
        thread_list.append(sent_thread)
        thread_list.append(loca_thread)

        # Lock
        lock = threading.Lock()
        lock.acquire()

        # Thread start
        for thread in thread_list:
            thread.start()
            time.sleep(0.1)
        
        # Thread stop
        lock.release()
        for thread in thread_list:
            thread.join()

        # prepare output
        numbering = 1
        out = ""
        for text in self.status_text:
            out += f"{numbering} : {text}\n\n"
            numbering += 1
        return out

    # main func
    def main(self, key, start_date, stop_date):
        start_time = time.time()
        dates = self.time.timerange(start_date, stop_date)
        print(dates)
        addr = self.path["search"]
        # Check for new key
        if not(os.path.exists(f"{addr}\\{key}")):
            os.mkdir(f"{addr}\\{key}")
            os.mkdir(f"{addr}\\{key}\\range")

        # Check for date that exist
        new_date = list()
        for date in dates:
            fdate = self.time.format_date(date)
            if not(os.path.exists(f"{addr}\\{key}\\{fdate}")):
                new_date.append(date)
        
        # If have new date
        if new_date:
            self.firstsearch(key, dates)
        
        text_out = self.range_func(key, start_date, stop_date)
        stop_time = time.time()
        print(f"main func : {stop_time-start_time} seconds")

        return text_out
    
    # Thread search func
    def thread_search(self, key, date):
        fdate = self.time.format_date(date)
        addr = self.path["search"]
        if not(os.path.exists(f"{addr}\\{key}\\{fdate}")):
            os.mkdir(f"{addr}\\{key}\\{fdate}")
        self.search(key, date)

    def texttool(self, text):
        etext = self.cut_emoji(text)
        ltext = etext.lower()
        if self.lang == "th":
            retool = re.compile(r'\s+')
            ltext = retool.sub('', ltext)
        retool = re.compile(r'(http[s]?://(?:[a-z]|[0-9]|[$-_!]|(?:%[0-9a-f][0-9a-f]))+)|([’][a-z])|[\[-`!-/:-@{-~\(\),\‘’…—^"]')
        fetext = retool.sub('',ltext)
        return fetext

    def cut_emoji(self, text):
        out = emoji.get_emoji_regexp().sub(u'', text)
        return out
    
    def clean_tag(self, data):
        ldata = data.lower()
        retool = re.compile(r'(#[a-zA-Zก-๙0-9]+)')
        cdata = retool.sub('',ldata)
        return cdata

    def add_word(self, words):
        if self.lang == "th":
            for word in words:
                self.th_word.add(word)
    
    def mkchart(self, key, data, fdate):
        matplotlib.font_manager.fontManager.addfont('c:\\users\\booma\\appdata\\local\\microsoft\\windows\\fonts\\thsarabunnew.ttf')
        matplotlib.rc("font", family="TH Sarabun New", size=25)
        label = list()
        size = list()
        count = 0
        for k, v in data.items():
            label.append(k)
            size.append(v)
            count += 1
            if count == 3:
                break
        # fig, ax = plt.subplots()
        plt.bar(label, size)
        plt.title(f"{key}")
        addr = self.path["search"]
        plt.savefig(f"{addr}\\{key}\\{fdate}\\chart.png")
        plt.clf()
    
    def mkchart_range(self, key, data, start, stop):
        fstart = self.time.format_date(start)
        fstop = self.time.format_date(stop)
        addr = self.path["search"]
        try:
            os.mkdir(f"{addr}\\{key}\\range")
        except FileExistsError:
            pass
        matplotlib.font_manager.fontManager.addfont('c:\\users\\booma\\appdata\\local\\microsoft\\windows\\fonts\\thsarabunnew.ttf')
        matplotlib.rc("font", family="TH Sarabun New", size=25)
        label = list()
        size = list()
        count = 0
        for k, v in data.items():
            label.append(k)
            size.append(v)
            count += 1
            if count == 3:
                break
        # fig, ax = plt.subplots()
        plt.bar(label, size)
        plt.title(f"{key}")
        plt.savefig(f"{addr}\\{key}\\range\\{fstart}_{fstop}\\mostword.png")
        plt.clf()

    def mkpie(self, key, data, fdate):
        matplotlib.font_manager.fontManager.addfont('c:\\users\\booma\\appdata\\local\\microsoft\\windows\\fonts\\thsarabunnew.ttf')
        matplotlib.rc("font", family="TH Sarabun New", size=25)
        label = list()
        size = list()
        color = ["#aeed6f", "#f06c62", "#ede96f"]
        for k, v in data.items():
            label.append(k)
            size.append(v)

        fig, ax = plt.subplots()
        ax.pie(size, labels=label, startangle=90, colors=color)
        ax.axis("equal")
        plt.title(f"{key}")
        addr = self.path["search"]
        plt.savefig(f"{addr}\\{key}\\{fdate}\\sentiment.png")
        plt.clf()
    
    def mkpie_range(self, key, data, start, stop):
        fstart = self.time.format_date(start)
        fstop = self.time.format_date(stop)
        matplotlib.font_manager.fontManager.addfont('c:\\users\\booma\\appdata\\local\\microsoft\\windows\\fonts\\thsarabunnew.ttf')
        matplotlib.rc("font", family="TH Sarabun New", size=25)
        label = list()
        size = list()
        color = ["#aeed6f", "#f06c62", "#ede96f"]
        for k, v in data.items():
            label.append(k)
            size.append(v)

        fig, ax = plt.subplots()
        ax.pie(size, labels=label, startangle=90, colors=color)
        ax.axis("equal")
        plt.title(f"{key}")
        addr = self.path["search"]
        plt.savefig(f"{addr}\\{key}\\range\\{fstart}_{fstop}\\sentiment.png")
        plt.clf()

    # location : single
    def location(self, key, fdate):
        print(f"Now do : location({key}, {fdate})")
        """
        Save location from user's location and write frequency in .csv
        """
        addr = self.path["search"]
        result_df = pd.read_csv(f"{addr}\\{key}\\{fdate}\\result.csv", index_col=False, encoding="UTF-8")
        loca_list = list(result_df["location"])
        addresses = list()
        location_data = list()
        for lo in loca_list:
            if lo != None and str(lo).upper() != "NAN":
                if not(str(lo).upper() in addresses):
                    location_time_start = time.time()
                    geolocator = Nominatim(user_agent="test")
                    loca = geolocator.geocode(lo, timeout=None)
                    location_time_stop = time.time()
                    # print(location_time_stop-location_time_start)
                    if loca != None:
                        # print(loca.address)
                        single_location_data = {"location" : str(lo).upper(), "latitude" : loca.latitude, "longitude" : loca.longitude, "count" : 1}
                        location_data.append(single_location_data)
                else:
                    index = addresses.index(lo.upper())
                    location_data[index]["count"] += 1
        loca_df = pd.DataFrame(location_data, columns=["location", "latitude", "longitude", "count"])
        loca_df.to_csv(f"{addr}\\{key}\\{fdate}\\location.csv", encoding="UTF-8")
        print(f"Complete : location({key}, {fdate})")
    
    # location freq
    def make_marker(self, key, fdate):
        """
        Read location frequency
        """
        addr = self.path["search"]
        location_df = pd.read_csv(f"{addr}\\{key}\\{fdate}\\location.csv", encoding="UTF-8")
        name_list = list(location_df["location"])
        lat_list = list(location_df["latitude"])
        long_list = list(location_df["longitude"])
        count_list = list(location_df["count"])
        self.location_data = list()
        for i in range(len(name_list)):
            single_location_data = {"location" : name_list[i],
                                    "latitude" : lat_list[i],
                                    "longtitude" : long_list[i],
                                    "count" : count_list[i]}
            self.location_data.append(single_location_data)

    def make_marker_range(self, key, start, stop):
        """
        Group all frequencies up into one group and make marker
        """
        dates = self.time.timerange(start, stop)

        # Create Threads
        lock = threading.Lock()
        list_threads = list()
        for date in dates:
            fdate = self.time.format_date(date)
            map_t = threading.Thread(target=self.make_marker, args=(key, fdate))
            list_threads.append(map_t)
        # Threads start
        lock.acquire()
        for map_t in list_threads:
            map_t.start()
            time.sleep(0.1)
        lock.release()
        for map_t in list_threads:
            map_t.join()
        # Threads stop

        location_dict = dict()
        for dic in self.location_data:
            if dic["location"] in location_dict:
                location_dict[dic["location"]]["count"] += int(dic["count"])
            else:
                location_dict[dic["location"]] = {"latitude" : dic["latitude"], "longtitude" : dic["longtitude"], "count" : dic["count"]}
            print(location_dict)
        for location in location_dict:
            print(location)
            if int(location_dict[location]["count"]) <= 5:
                color = "green"
            elif int(location_dict[location]["count"]) <= 10:
                color = "orange"
            else:
                color = "red"
            marker = folium.Marker(location=[location_dict[location]["latitude"], location_dict[location]["longtitude"]], 
                                    popup=f"<b>{location}</b>",
                                    icon=folium.Icon(color=color, icon="info-sign"))
            marker.add_to(self.map)
        return self.map

    def update(self):
        addr = self.path["search"]
        for lang in os.listdir(addr):
            for key in os.listdir(f"{addr}\\{lang}"):
                self.search(key)

def main():
    twee = TwitterAPI()
    twee.update()

if __name__ == "__main__":
    # main()
    tweep = TwitterAPI()
