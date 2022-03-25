import requests
from bs4 import BeautifulSoup
import datetime
import pythainlp.tokenize
import nltk
import pandas as pd
import re
from timestamp import Timestamp
import os
import json
from sentiment import Sentiment
from textblob import TextBlob
import matplotlib
import matplotlib.pyplot as plt
import time
import threading

# Web Crawier
class News(object):

    # Define url, keyword, request html
    def __init__(self, lang="en"):
        self.sent = Sentiment()
        self.lang = lang
        self.web_list = list()
        self.keyword = ""
        self.req = None
        self.element = None
        self.html = None
        self.thnlp = pythainlp.tokenize
        self.ennlp = nltk
        self.time = Timestamp()
        self.wd_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.path = f"{self.wd_path}\\src\\web" # Enter file path
        self.setup_weblist()

    def setup_weblist(self):
        f = open(f"{self.wd_path}\\py\\foo.json", "r", encoding="UTF-8")
        raw = f.read()
        self.web_list = json.loads(raw)

    # Request search html
    def search(self, fdate):
        try:
            f = open(f"{self.path}\\{fdate}.csv", "r", encoding="UTF-8")
            f.close()
        except FileNotFoundError:
            df_list = list()
            for domain in self.web_list.keys():
                for web in self.web_list[domain]:
                    try:
                        self.req = requests.get(web, timeout=10)
                        self.element = self.req.text
                        if self.element:
                            self.html = BeautifulSoup(self.element, "html.parser")
                            elem_lines = self.html.find_all('a')
                            print(domain)
                            print(web)
                            if elem_lines:
                                for line in elem_lines:
                                    text = line.get_text()
                                    if self.analyze(text):
                                        retool = re.compile(r'\n|\t|\s{2,}')
                                        text = retool.sub('', text)
                                        href = str(line.get('href'))
                                        if href[0] == 'h':
                                            query = href
                                        else:
                                            query = web + href
                                        web_dict = {
                                                    "domain" : domain,
                                                    "web" : web,
                                                    "text" : text,
                                                    "query" : query
                                                    }
                                        print(web_dict)
                                        df_list.append(web_dict)
                    except:
                        continue
            web_df = pd.DataFrame(df_list)
            web_df.to_csv(f"{self.path}\\result\\{fdate}.csv", encoding="UTF-8")
    
    def search_file(self, key):
        """
        Search through all available file.
        If key match, return with text, query and filename.
        """
        start_time = time.time()
        self.match_key = list()
        self.match_domain = dict()
        dir_time = os.listdir(f"{self.path}\\result")

        # Thread
        for j in range(0, len(dir_time), 4):
            print(f"j : {j}")
            if (j+4) > (len(dir_time)):
                for k in range(len(dir_time)):
                    print(f"k : {k}")
                    self.thread_main(dir_time[j+k], key)
            else:
                print("thread")
                thread_list = list()
                # Create Threads
                for k in range(4):
                    t = threading.Thread(target=self.thread_main, args=(dir_time[j+k], key))
                    thread_list.append(t)
                
                lock = threading.Lock()
                lock.acquire()
                # Thread start
                for thread in thread_list:
                    thread.start()
                    time.sleep(0.1)
                lock.release()
                # Thread stop
                for thread in thread_list:
                    thread.join()
                print("thread stop")

        # Sentiment Analysis
        sentiment_news = {"pos" : 0, "neg" : 0, "neu" : 0}
        out = ""
        for item in self.match_key:
            text = item
            if pythainlp.util.isthai(text):
                tag = self.sent.classify(text)
                sentiment_news[tag] += 1
            else:
                tag = TextBlob(text).sentiment.polarity
                if tag > 0:
                    sentiment_news["pos"] += 1
                elif tag < 0:
                    sentiment_news["neg"] += 1
                else:
                    sentiment_news["neu"] += 1
            # Field output
            out += f"{item}\n\n"
        # Make a sentiment chart
        matplotlib.font_manager.fontManager.addfont('c:\\users\\booma\\appdata\\local\\microsoft\\windows\\fonts\\thsarabunnew.ttf')
        matplotlib.rc("font", family="TH Sarabun New", size=25)
        label = list()
        size = list()
        color = ["#aeed6f", "#f06c62", "#ede96f"]
        for k, v in sentiment_news.items():
            label.append(k)
            size.append(v)

        fig, ax = plt.subplots()
        ax.pie(size, labels=label, startangle=90, colors=color)
        ax.axis("equal")
        plt.title(f"{key}")
        plt.savefig(f"{self.path}\\sentiment.png")
        plt.clf()

        # Most domain
        match_domain = dict(sorted(self.match_domain.items(), key=lambda item:item[1], reverse=True))
        domain_name = list()
        domain_freq = list()
        count = 0
        for k,v in match_domain.items():
            domain_name.append(k)
            domain_freq.append(v)
            count += 1
            if count == 3:
                break
        
        plt.bar(domain_name, domain_freq)
        plt.title(f"{key}")
        plt.savefig(f"{self.path}\\mostdomain.png")
        plt.clf()
        stop_time = time.time()
        print(f"news time : {stop_time-start_time}")
        return out

    # main code
    def thread_main(self, filename, key):
        print(f"Now do : thread_main({filename}, {key}")
        df = pd.read_csv(f"{self.path}\\result\\{filename}", encoding="UTF-8")
        texts = list(df["text"])
        domains = list(df["domain"])
        for i in range(len(texts)):
            text = str(texts[i])
            first_tokenized = nltk.word_tokenize(text)
            tokenized_word = list()
            for tokenized in first_tokenized:
                if pythainlp.util.isthai(tokenized):
                    second_tokenized = pythainlp.tokenize.word_tokenize(tokenized)
                    _add = [item for item in second_tokenized]
                    tokenized_word += _add
                else:
                    tokenized_word.append(tokenized)
            
            for word in tokenized_word:
                if key.lower() == word.lower():
                    self.match_key.append(text)
                    if domains[i] in self.match_domain:
                        self.match_domain[domains[i]] += 1
                    else:
                        self.match_domain[domains[i]] = 1
        print(f"Complete : thread_main({filename}, {key})")

    # Change language
    def ch_lang(self, lang):
        self.lang = lang
    
    # Check is sentence
    def analyze(self, text):
        if self.lang == "en":
            size = len(self.ennlp.word_tokenize(text))
            if size >= 4:
                return True
            else:
                return False
        else:
            size = len(self.thnlp.word_tokenize(text, engine="newmm", keep_whitespace=False))
            if size >= 5:
                return True
            else:
                return False
    
    # get new file
    def update(self):
        date = self.time.get_date_now()
        fdate = self.time.format_date(date)
        self.search(fdate)
            
def main():
    news = News()
    news.update()

if __name__ == "__main__":
    main()