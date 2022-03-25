from nltk import NaiveBayesClassifier as nbc
from pythainlp.tokenize import word_tokenize
import codecs
from itertools import chain
import pickle
import time
import os

class Sentiment(object):
    def __init__(self):
        self.wd_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.path = f"{self.wd_path}\\py"
        self.set_pos()
        self.set_neg()
        self.set_neu()
        self.set_vocabulary()
        self.set_classifier()

    def set_pos(self):
        with codecs.open(f"{self.path}\\pos.txt", "r", encoding="UTF-8") as f:
            lines = f.readlines()
        self.listpos=[e.strip() for e in lines]
        f.close()

    def set_neg(self):
        with codecs.open(f"{self.path}\\neg.txt", "r", encoding="UTF-8") as f:
            lines = f.readlines()
        self.listneg=[e.strip() for e in lines]
        f.close() 

    def set_neu(self):
        with codecs.open(f"{self.path}\\neu.txt", "r", encoding="UTF-8") as f:
            lines = f.readlines()
        self.listneu=[e.strip() for e in lines]
        f.close()
    
    def set_classifier(self):
        try:
            self.classifier = pickle.load(open(f"{self.path}\\sentiment_classifier.pkl","rb"))
        except FileNotFoundError:
            return -1
    
    def set_vocabulary(self):
        pos1=['pos']*len(self.listpos)
        neg1=['neg']*len(self.listneg)
        neu1=['neu']*len(self.listneu)
        self.training_data = list(zip(self.listpos,pos1)) + list(zip(self.listneg,neg1)) + list(zip(self.listneu,neu1))
        self.vocabulary = set(chain(*[word_tokenize(i[0].lower()) for i in self.training_data]))

    def train(self):
        self.set_vocabulary()
        feature_set = [({i:(i in word_tokenize(sentence.lower())) for i in self.vocabulary},tag) for sentence, tag in self.training_data]
        self.classifier = nbc.train(feature_set)
        pickle.dump(self.classifier, open(f"{self.path}\\sentiment_classifier.pkl","wb"))
    
    def classify(self, test_sentence):
        token_start =  time.time()
        tokenized_word = word_tokenize(test_sentence.lower(), engine="newmm", keep_whitespace=False)
        token_stop = time.time()
        print(f"tokenize time : {token_stop-token_start}")
        featurized_test_sentence = dict()
        bool_time_start = time.time()
        for vocab in self.vocabulary:
            _bool = vocab in tokenized_word
            featurized_test_sentence[vocab] = _bool
        bool_time_stop = time.time()
        print(f"dict time : {bool_time_stop-bool_time_start}")
        class_start = time.time()
        result = self.classifier.classify(featurized_test_sentence) # ใช้โมเดลที่ train ประมวลผล
        class_stop = time.time()
        print(f"classify time : {class_stop-class_start}")
        # print(featurized_test_sentence)
        return result

if __name__ == "__main__":
    sent = Sentiment()
    start = time.time()
    print(sent.classify("""สบายดีไหม"""))
    stop = time.time()
    print(f"class func time : {stop-start}")
    start = time.time()
    print(sent.classify("""ม็อบของสลิ่มที่หน้าหอศิลป์ค่ะเราเห็นตอนที่พี่เขาโดนล็อคคอแล้วโดนต่อยเราไม่ทราบเหตุการณ์ก่อนหน้านี้ว่าเกิดอะไรขึ้น"""))
    stop = time.time()
    print(f"class func time : {stop-start}")
    # sent.train()