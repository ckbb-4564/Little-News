import requests
from bs4 import BeautifulSoup
import os
import json
import concurrent.futures

all_list =["https://apnews.com/",
            "https://news.google.com/topstories?hl=en-US&gl=US&ceid=US:en",
            "https://www.nationthailand.com/",
            "https://www.nbcnews.com/",
            "https://www.nytimes.com/",
            "https://abcnews.go.com/"
            "https://www.nbcnews.com/",
            "https://www.huffpost.com/",
            "https://www.nbcnews.com/",
            "https://www.cbsnews.com/",
            "https://www.usatoday.com/",
            "https://www.nytimes.com/",
            "https://www.foxnews.com/",
            "https://www.dailymail.co.uk/ushome/index.html/"
            "https://www.businessinsider.com/",
            "https://elitedaily.com/",
            "https://www.cnet.com/",
            "https://www.cnbc.com/world/?region=world/",
            "https://www.marketwatch.com/",
            "https://www.investing.com/",
            "https://www.bangkokpost.com/",
            "https://www.cnet.com/",
            "https://www.theguardian.com/us/"
            "https://www.msn.com/en-us/news/",
            "https://www.npr.org/",
            "https://www.nydailynews.com/",
            "https://www.latimes.com/",
            "https://nypost.com/",
            "https://time.com/,",
            "https://mashable.com/",
            "https://www.sfgate.com/",
            "https://www.slate.com/",
            "https://www.upworthy.com/",
            "https://www.theblaze.com/",
            "https://www.telegraph.co.uk/",
            "https://www.vice.com/en_us/",
            "https://www.chron.com/",
            "https://gawker.com/",
            "https://www.vox.com/",
            "https://www.chicagotribune.com/",
            "https://www.thedailybeast.com/",
            "https://www.salon.com/",
            "https://mic.com/",
            "https://www.mirror.co.uk/news/",
            "https://www.nj.com/",
            "https://www.independent.co.uk/",
            "https://www.freep.com/",
            "https://www.bostonglobe.com/",
            "https://www.theatlantic.com/",
            "https://www.mlive.com/",
            "https://www.engadget.com/",
            "https://techcrunch.com/",
            "https://www.boston.com/",
            "https://www.al.com/",
            "https://www.sanook.com/news/",
            "https://www.thairath.co.th/news",
            "https://www.komchadluek.net/",
            "http://www.chiangmainews.co.th/",
            "http://www.matichon.co.th/",
            "http://www.dailynews.co.th/",
            "http://naewna.com/",
            "http://www.bangkokbiznews.com/",
            "http://www.khaosodusa.com/",
            "http://www.manager.co.th/",
            "http://www.thannews.th.com/",
            "http://www.siamturakij.com/",
            "http://www.bangkokpost.com/",
            "http://www.thaipost.net/",
            "http://www.nationmultimedia.com/",
            "http://www.komchadluek.com/",
            "http://www.sentang.com/",
            "http://www.siamsport.co.th/",
            "http://www.thaitv3.com/",
            "http://www.tv5.co.th/",
            "http://www.ch7.com/",
            "http://www.prd.go.th/",
            "http://www.samarts.com/"]

def threadfunc(url, progress):
    output = list()
    try:
        req = requests.get(url)
        ele = req.text
        html = BeautifulSoup(ele, "html.parser")
        elem_lines = html.find_all('a', href=True)
        output.append(url)
        for line in elem_lines:
            href = str(line.get('href'))
            if len(href) == 0:
                    continue
            if href[0] == 'h':
                    link = href
            else:
                    link = url + href

            if not(link in output):
                print(progress)
                print(link)
                output.append(link)

                try:
                    _req = requests.get(link)
                    _ele = _req.text
                    _html = BeautifulSoup(_ele, "html.parser")
                    _elem_lines = _html.find_all('a', href=True)
                    for _line in _elem_lines:
                        _href = str(_line.get('href'))
                        if len(_href) == 0:
                            continue
                        if _href[0] == 'h':
                                _link = _href
                        else:
                                _link = url + _href
                        if not(_link in output):
                            print(progress)
                            print(_link)
                            output.append(_link)
                except:
                    continue
    except:
        pass
    return output

all_link = list()
N = 10
web_dict = dict()
for i in range(0, len(all_list), N):
    thread_list = list()
    with concurrent.futures.ThreadPoolExecutor() as thread:
        for j in range(N):
            if (i+j) >= len(all_list):
                break
            else:
                progress = f"{i+j+1} / 10"
                worker = thread.submit(threadfunc, all_list[i+j], progress)
                thread_list.append(worker)
            for t in range(len(thread_list)):
                return_val = thread_list[t].result()
                web_dict[all_list[i+t]] = return_val  
    
j = json.dumps(web_dict)
f = open(r'C:\Users\booma\Desktop\backup\API_Crawler\py\foo.json', 'w', encoding='UTF-8')
f.write(j)
f.close()