import time
import_start_time = time.time()
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QDate, QObject, QThread, pyqtSignal
from twitter import TwitterAPI
from news import News
from timestamp import Timestamp
import sys
import folium
import io
from PyQt5 import QtWebEngineWidgets
from invest import Invest
from functools import *
import os
from IPython.core.display import HTML
import_stop_time = time.time()
print(f"import time : {import_stop_time-import_start_time}")


class Ui_LittleNews(object):
    def __init__(self):
        self.api = TwitterAPI()
        self.web = News()
        self.time = Timestamp()
        self.invest = Invest()
        self.wd_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.default_path = f"{self.wd_path}\\src"
        self.path = {
                    "logo" : f"{self.default_path}\\index\\logo.png",
                    "in app logo" : f"{self.default_path}\\index\\applogo.png",
                    "uk flag" : f"{self.default_path}\\index\\UKflag.webp",
                    "th flag" : f"{self.default_path}\\index\\THflag.png",
                    "de_chart" : f"{self.default_path}\\index\\applogo.png",
                    "chart" : f"{self.default_path}\\twitter\\search\\",
                    "demo_map" : f"{self.default_path}\\index\\demomap.png"
                    }
        self.setup_dir()

    def setupUi(self, LittleNews):
        # # # # MAIN WINDOW SETUP # # # #
        LittleNews.setGeometry(0, 0, 1900, 1000)
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        # sizePolicy.setHeightForWidth(LittleNews.sizePolicy().hasHeightForWidth())
        # LittleNews.setSizePolicy(sizePolicy)
        LittleNews.setMaximumSize(QtCore.QSize(1900, 1000))
        LittleNews.setWindowTitle("LittleNews")

        bg_color = "rgb(21,32,43)"
        field_color = "rgb(35,32,52)"
        white = "rgb(255,255,255)"
        black = "rgb(0,0,0)" 
        font = 'font: 16pt "TH Sarabun New"'
       
       # # # # ICON # # # #
        window_icon = QtGui.QIcon()
        window_icon.addPixmap(QtGui.QPixmap(self.path["logo"]), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        LittleNews.setWindowIcon(window_icon)
        LittleNews.setStyleSheet(f"background:{bg_color}")

        self.centralwidget = QtWidgets.QWidget(LittleNews)

        # # # # SCREEN # # # #
        self.layout = QtWidgets.QWidget(self.centralwidget)
        self.layout.setGeometry(QtCore.QRect(10, 10, 1881, 966))

        # # # # WHOLE GRID # # # #
        self.grid_box = QtWidgets.QGridLayout(self.layout)
        self.grid_box.setContentsMargins(0, 0, 0, 0)

        # # # TREND LAYOUT # # #
        self.trends_box = QtWidgets.QVBoxLayout()
        self.trends_box.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        
        # # APP LOGO # #
        self.logo = QtWidgets.QLabel(self.layout)
        self.logo.setMinimumSize(QtCore.QSize(159, 120))
        self.logo.setMaximumSize(QtCore.QSize(159, 120))
        self.logo.setPixmap(QtGui.QPixmap(self.path["in app logo"]))
        self.logo.setScaledContents(True)
        # # END APP LOGO # #

        # # TODAY'S TRENDS # #
        self.trend_label = QtWidgets.QLabel(self.layout)
        # self.trend_label.setMaximumSize(QtCore.QSize(159, 30))
        self.trend_label.setStyleSheet(f"{font};color:{white}")
        self.trend_label.setTextFormat(QtCore.Qt.PlainText)
        self.trend_label.setAlignment(QtCore.Qt.AlignCenter)
        self.trend_label.setText("Today\'s Trends")
        # # END TODAY'S TRENDS # #

        # # DISPLAY TRENDS # #
        self.trend_field = QtWidgets.QListWidget(self.layout)
        # self.trend_field.setMaximumSize(QtCore.QSize(159, 600))
        self.trend_field.setStyleSheet(f"{font};color:{white};background-color:{field_color}")
        # # END DISPLAY TRENDS # #
        
        self.trends_box.setStretch(2, 200)
        self.trends_box.addWidget(self.logo)
        self.trends_box.addWidget(self.trend_label)
        self.trends_box.addWidget(self.trend_field)
        # # # END TREND LAYOUT # # #

        # # # SEARCH LAYOUT # # #
        self.searchbox = QtWidgets.QHBoxLayout()
        # self.searchbox.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        
        # # SEARCH LABEL # #
        self.search_label = QtWidgets.QLabel(self.layout)
        self.search_label.setStyleSheet(f"{font};color:{white}")
        self.search_label.setAlignment(QtCore.Qt.AlignCenter)
        self.search_label.setText("Search")
        # # END SEARCH LABEL # #

        # # SEARCH ENTRY # #
        self.search_entry = QtWidgets.QLineEdit(self.layout)
        self.search_entry.setStyleSheet(f"{font};color:{white}")
        # # END SEARCH ENTRY # #

        # # SEARCH BUTTON # #
        self.search_btn = QtWidgets.QPushButton(self.layout)
        self.search_btn.setStyleSheet(f"{font};color:{black};background-color:{white}")
        self.search_btn.setText("Go")
        self.search_btn.clicked.connect(self.search_func)
        # # END SEARCH BUTTON # #

        # # DATE GRID # #
        self.date_grid = QtWidgets.QGridLayout()

        # SINCE LABEL #
        self.since_label = QtWidgets.QLabel(self.layout)
        self.since_label.setStyleSheet(f"{font};color:{white}")
        self.since_label.setAlignment(QtCore.Qt.AlignCenter)
        self.since_label.setText("Since")
        # END SINCE LABEL #

        # UNTIL LABEL #
        self.until_label = QtWidgets.QLabel(self.layout)
        self.until_label.setStyleSheet(f"{font};color:{white}")
        self.until_label.setAlignment(QtCore.Qt.AlignCenter)
        self.until_label.setText("Until")
        # END UNTIL LABEL #

        # SINCE DATE EDIT #
        self.sincedate = QtWidgets.QDateEdit(self.layout)
        # self.sincedate.setMaximumSize(QtCore.QSize(250, 20))
        self.sincedate.setStyleSheet(f"background:{white};{font};color:{black}")
        self.sincedate.setCalendarPopup(True)
        today = self.time.get_date_now()
        self.sincedate.setDate(QDate(int(today.year), int(today.month), int(today.day)))
        # END SINCE DATE EDIT #

        # UNTIL DATE EDIT #
        self.untildate = QtWidgets.QDateEdit(self.layout)
        # self.untildate.setMaximumSize(QtCore.QSize(250, 20))
        self.untildate.setStyleSheet(f"background:{white};{font};color:{black}")
        self.untildate.setCalendarPopup(True)
        self.untildate.setDate(QDate(int(today.year), int(today.month), int(today.day)))
        # END UNTIL DATE EDIT #

        # SPACER #
        self.spacer = QtWidgets.QSpacerItem(20, 200)
        # END SPACER #
        
        self.date_grid.addWidget(self.since_label, 0, 0, 1, 1)
        self.date_grid.addWidget(self.sincedate, 0, 1, 1, 1)
        self.date_grid.addWidget(self.until_label, 1, 0, 1, 1)
        self.date_grid.addWidget(self.untildate, 1, 1, 1, 1)
        # self.date_grid.addItem(self.spacer, 2, 0, 1, 1)
        # # END DATE GRID # #

        # # LANGUAGE GRID # #
        self.lang_grid = QtWidgets.QGridLayout()
        # self.lang_grid.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        # self.lang_grid.setContentsMargins(-1, 0, -1, -1)

        # UK FLAG #
        self.uk_flag = QtWidgets.QPushButton(self.layout)
        self.uk_flag.setMaximumSize(QtCore.QSize(40, 20))
        self.uk_flag.setFlat(True)
        self.uk_flag.setIcon(QtGui.QIcon(self.path["uk flag"]))
        self.uk_flag.setIconSize(QtCore.QSize(40,20))
        self.uk_flag.clicked.connect(lambda:self.do_chlang("en"))
        # END UK FLAG #

        # TH FLAG #
        self.th_flag = QtWidgets.QPushButton(self.layout)
        self.th_flag.setMaximumSize(QtCore.QSize(40, 20))
        self.th_flag.setFlat(True)
        self.th_flag.setIcon(QtGui.QIcon(self.path["th flag"]))
        self.th_flag.setIconSize(QtCore.QSize(50,25))
        self.th_flag.clicked.connect(lambda:self.do_chlang("th"))
        # END TH FLAG #
        
        # TH TEXT #
        self.th_label = QtWidgets.QLabel(self.layout)
        self.th_label.setStyleSheet(f"{font};color:{white}")
        self.th_label.setAlignment(QtCore.Qt.AlignCenter)
        self.th_label.setText("TH")
        # END TH TEXT #
        
        # EN TEXT #
        self.en_label = QtWidgets.QLabel(self.layout)
        self.en_label.setStyleSheet(f"{font};color:{white}")
        self.en_label.setAlignment(QtCore.Qt.AlignCenter)
        self.en_label.setText("EN")
        # END EN TEXT #

        self.lang_grid.addWidget(self.uk_flag, 0, 0, 1, 1)
        self.lang_grid.addWidget(self.th_flag, 0, 1, 1, 1)
        self.lang_grid.addWidget(self.th_label, 1, 1, 1, 1)
        self.lang_grid.addWidget(self.en_label, 1, 0, 1, 1)
        # # END LANGUAGE GRID # #

        self.searchbox.addWidget(self.search_label)
        self.searchbox.addWidget(self.search_entry)
        self.searchbox.addWidget(self.search_btn)
        self.searchbox.addLayout(self.date_grid)
        self.searchbox.addLayout(self.lang_grid)
        # self.searchbox.setStretch(1, 10)
        # # # END SEARCH LAYOUT # # #

        # # # NEWS GRID # # #
        self.news_box = QtWidgets.QGridLayout()

        # # TAB # #
        self.tab_field = QtWidgets.QTabWidget(self.layout)
        self.tab_field.setMaximumSize(QtCore.QSize(1613, 449))
        self.tab_field.setMinimumSize(QtCore.QSize(1613, 449))

        # TWITTER TAB
        self.twit_tab = QtWidgets.QWidget()
        self.twit_layout_wid = QtWidgets.QWidget(self.twit_tab)
        self.twit_layout_wid.setGeometry(-10, -10, 1613, 449)
        self.twit_layout = QtWidgets.QHBoxLayout(self.twit_layout_wid)

        # NEWS TAB
        self.news_tab = QtWidgets.QWidget()
        self.news_layout_wid = QtWidgets.QWidget(self.news_tab)
        self.news_layout_wid.setGeometry(-10, -10, 1613, 449)
        self.news_layout = QtWidgets.QHBoxLayout(self.news_layout_wid)

        # # WEB DISPLAY # #
        self.web_field = QtWidgets.QTextBrowser(self.news_layout_wid)
        self.web_field.setMaximumSize(QtCore.QSize(709, 449))
        self.web_field.setMinimumSize(QtCore.QSize(709, 449))
        self.web_field.setStyleSheet(f"{font};color:{white};background-color:{field_color}")

        self.web_chart = QtWidgets.QLabel(self.news_layout_wid)
        self.web_chart.setMinimumSize(QtCore.QSize(449, 449))
        self.web_chart.setMaximumSize(QtCore.QSize(449, 449))
        self.web_chart.setPixmap(QtGui.QPixmap(self.path["de_chart"]))
        self.web_chart.setScaledContents(True)

        self.web_sent = QtWidgets.QLabel(self.news_layout_wid)
        self.web_sent.setMinimumSize(QtCore.QSize(449, 449))
        self.web_sent.setMaximumSize(QtCore.QSize(449, 449))
        self.web_sent.setPixmap(QtGui.QPixmap(self.path["de_chart"]))
        self.web_sent.setScaledContents(True)

        self.news_layout.addWidget(self.web_field)
        self.news_layout.addWidget(self.web_chart)
        self.news_layout.addWidget(self.web_sent)
        # # END WEB DISPLAY # #
        
        # # TWITTER DISPLAY # #
        self.twitter_field = QtWidgets.QTextBrowser(self.twit_layout_wid)
        self.twitter_field.setMaximumSize(QtCore.QSize(1158, 449))
        self.twitter_field.setMinimumSize(QtCore.QSize(1158, 449))
        self.twitter_field.setStyleSheet(f"{font};color:{white};background-color:{field_color}")

        self.twitter_sent = QtWidgets.QLabel(self.twit_layout_wid)
        self.twitter_sent.setMinimumSize(QtCore.QSize(449, 449))
        self.twitter_sent.setMaximumSize(QtCore.QSize(449, 449))
        self.twitter_sent.setPixmap(QtGui.QPixmap(self.path["de_chart"]))
        self.twitter_sent.setScaledContents(True)

        self.twit_layout.addWidget(self.twitter_field)
        self.twit_layout.addWidget(self.twitter_sent)
        # # END TWITTER DISPLAY # #

        self.tab_field.addTab(self.twit_tab, "Twitter")
        self.tab_field.addTab(self.news_tab, "Website")
        # # END TAB # #

        # # INVEST LAYOUT # #
        self.invest_layout = QtWidgets.QHBoxLayout()

        # INVEST RESULT #
        self.invest_result = QtWidgets.QVBoxLayout()

        # INVEST SEARCH #
        self.invest_search = QtWidgets.QHBoxLayout()

        self.invest_label = QtWidgets.QLabel(self.layout)
        self.invest_label.setStyleSheet(f"{font};color:{white}")
        self.invest_label.setAlignment(QtCore.Qt.AlignCenter)
        self.invest_label.setText("Invest")

        self.invest_entry = QtWidgets.QLineEdit(self.layout)
        self.invest_entry.setStyleSheet(f"{font};color:{white}")

        self.invest_btn = QtWidgets.QPushButton(self.layout)
        self.invest_btn.setStyleSheet(f"{font};color:{black};background-color:{white}")
        self.invest_btn.setText("Go")
        self.invest_btn.clicked.connect(self.do_invest)

        self.invest_search.addWidget(self.invest_label)
        self.invest_search.addWidget(self.invest_entry)
        self.invest_search.addWidget(self.invest_btn)
        # END INVEST SEARCH #

        self.invest_graph = QtWebEngineWidgets.QWebEngineView(self.layout)
        self.invest_graph.setMaximumSize(QtCore.QSize(701, 416))

        self.invest_result.addLayout(self.invest_search)
        self.invest_result.addWidget(self.invest_graph)
        # END INVEST RESULT #

        self.key_chart = QtWidgets.QLabel(self.layout)
        self.key_chart.setMaximumSize(QtCore.QSize(449, 449))
        self.key_chart.setPixmap(QtGui.QPixmap(self.path["de_chart"]))
        self.key_chart.setScaledContents(True)
        self.key_chart.setUpdatesEnabled(True)

        self.invest_layout.addLayout(self.invest_result)
        self.invest_layout.addWidget(self.key_chart)
        # # END INVEST LAYOUT # #

        # # HEAT MAP # #
        self.map = QtWebEngineWidgets.QWebEngineView(self.layout)
        self.map.setMinimumSize(QtCore.QSize(449, 449))
        self.invest_layout.addWidget(self.map)
        # # END HEAT MAP # #

        self.news_box.addWidget(self.tab_field, 0, 0, 1, 1)
        # # # END NEWS GRID # # #

        self.grid_box.addLayout(self.trends_box, 0, 0, 4, 1)
        self.grid_box.addLayout(self.searchbox, 0, 1, 1, 1)
        self.grid_box.addLayout(self.news_box, 1, 1, 1, 1)
        self.grid_box.addLayout(self.invest_layout, 2, 1, 1, 1)
        self.grid_box.setColumnStretch(1, 1000)
        # # # # END WHOLE GRID # # # #

        LittleNews.setCentralWidget(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(LittleNews)
        self.do_trend()
        self.set_init_map()
        # now = self.time.get_date_now()
        # fdate = self.time.format_date(now)
        # self.web.search(fdate)

    def search_func(self):
        # Test for timerange enable
        start = self.sincedate.date().toString(Qt.ISODate)
        stop = self.untildate.date().toString(Qt.ISODate)
        if self.time.timerange(start, stop) != -1:
            tab_index = self.get_tabIndex()
            if tab_index == 0:
                self.do_twitter_search()
            else:
                self.do_web_search()
        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Date Error")
            msg.setInformativeText('Your Until date is greater than today or your Since date is greater than your Until date.')
            msg.setWindowTitle("Error")
            msg.exec_()
    
    def do_twitter_search(self):
        # get search query
        query = self.search_entry.text()   
        start = self.sincedate.date().toString(Qt.ISODate)
        stop = self.untildate.date().toString(Qt.ISODate)

        # QThread Zone
        self.twit_thread = QThread()
        self.twit_worker = Worker()
        self.twit_worker.moveToThread(self.twit_thread)
        twit_search_partial = partial(self.twit_worker.twit_search, query, start, stop)
        self.twit_thread.started.connect(twit_search_partial)
        self.twit_worker.finished.connect(self.twit_thread.quit)
        self.twit_worker.finished.connect(self.twit_worker.deleteLater)
        self.twit_thread.finished.connect(self.twit_thread.deleteLater)
        
        # update mostword
        up_chart_func = partial(self.update_chart, query, start, stop)
        self.twit_thread.finished.connect(up_chart_func)

        # update sentiment
        up_sent_func = partial(self.update_sent, query, start, stop)
        self.twit_thread.finished.connect(up_sent_func)

        # update display field
        self.twit_worker.twit_progress.connect(self.set_twit_text)
        self.twit_worker.map_progress.connect(self.update_map)

        self.twit_thread.start()

    def do_web_search(self):
        # get search query
        query = self.search_entry.text()
        start = self.untildate.date().toString(Qt.ISODate)
        stop = self.sincedate.date().toString(Qt.ISODate)
        
        # QThread
        self.web_thread = QThread()
        self.web_worker = Worker()
        self.web_worker.moveToThread(self.web_thread)
        web_search_partial = partial(self.web_worker.web_search, query, self.web.lang)
        self.web_thread.started.connect(web_search_partial)
        self.web_worker.finished.connect(self.web_thread.quit)
        self.web_worker.finished.connect(self.web_worker.deleteLater)
        self.web_thread.finished.connect(self.web_thread.deleteLater)

        # update sentiment
        self.web_thread.finished.connect(self.update_web_sent)
        self.web_thread.finished.connect(self.update_mostdomain)

        # update display field
        self.web_worker.web_progress.connect(self.set_web_text)

        self.web_thread.start()

    def set_search_entry(self):
        text = self.trend_field.currentItem().text()
        self.search_entry.setText(text)

    # Invest graph
    def do_invest(self):
        start = self.untildate.date().toString(Qt.ISODate)
        stop = self.sincedate.date().toString(Qt.ISODate)
        if self.time.is_timerange_enable(start, stop):
            text = self.invest_entry.text()
            html = self.invest.get_data(text, stop, start)
            self.invest_graph.setHtml(html)
        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Date Error")
            msg.setInformativeText('Your Until date is greater than today or your Since date is greater than your Until date.')
            msg.setWindowTitle("Error")
            msg.exec_()
    
    def do_chlang(self, lang):
        self.api.ch_lang(lang)
        self.web.ch_lang(lang)
        self.do_trend()
    
    def do_trend(self):
        trends = self.api.show_trend()
        self.trend_field.clear()
        for trend in trends:
            self.trend_field.addItem(trend)
        self.trend_field.itemClicked.connect(self.set_search_entry)
    
    def update_chart(self, key, start, stop):
        fstart = self.time.format_date(start)
        fstop = self.time.format_date(stop)
        addr = self.path["chart"]
        url = f"{addr}\\{key}\\range\\{fstart}_{fstop}\\mostword.png"
        pixmap = QtGui.QPixmap(url)
        self.key_chart.setPixmap(pixmap)
    
    def update_sent(self, key, start, stop):
        fstart = self.time.format_date(start)
        fstop = self.time.format_date(stop)
        addr = self.path["chart"]
        twit_url = f"{addr}\\{key}\\range\\{fstart}_{fstop}\\sentiment.png"
        self.twitter_sent.setPixmap(QtGui.QPixmap(twit_url))
    
    def update_web_sent(self):
        url = f"{self.default_path}\\web\\sentiment.png"
        self.web_sent.setPixmap(QtGui.QPixmap(url))
    
    def set_init_map(self):
        m = folium.Map(location=(0,0), zoom_start=1, tiles='Stamen Terrain')
        data = io.BytesIO()
        m.save(data, close_file=False)
        temp = data.getvalue().decode()
        self.map.setHtml(data.getvalue().decode())

    def update_map(self, m):
        data = io.BytesIO()
        m.save(data, close_file=False)
        self.map.setHtml(data.getvalue().decode())
    
    def update_mostdomain(self):
        url = f"{self.default_path}\\web\\mostdomain.png"
        self.web_chart.setPixmap(QtGui.QPixmap(url))
    
    def set_twit_text(self, text):
        self.twitter_field.setText(text)
    
    def set_web_text(self, text):
        self.web_field.setText(text)
    
    def get_tabIndex(self):
        return self.tab_field.currentIndex()

    def setup_dir(self):
        if not(os.path.exists(f"{self.default_path}\\twitter")):
            os.mkdir(f"{self.default_path}\\twitter")
            os.mkdir(f"{self.default_path}\\twitter\\search")
            os.mkdir(f"{self.default_path}\\twitter\\trend")
        elif not(os.path.exists(f"{self.default_path}\\web")):
            os.mkdir(f"{self.default_path}\\web")
            os.mkdir(f"{self.default_path}\\web\\result")
    
class Worker(QObject):
    finished = pyqtSignal()
    twit_progress = pyqtSignal(str)
    web_progress = pyqtSignal(str)
    map_progress = pyqtSignal(object)

    def twit_search(self, key, start, stop):
        twee = TwitterAPI()
        twit_out = twee.main(key, start, stop)
        self.twit_progress.emit(twit_out)
        self.map_progress.emit(twee.map)
        self.finished.emit()
    
    def web_search(self, key, lang):
        web = News()
        web.ch_lang(lang)
        web_out = web.search_file(key)
        self.web_progress.emit(web_out)
        self.finished.emit()
    
    def invest_search(self, key):
        pass

def main():
    app = QtWidgets.QApplication(sys.argv)
    LittleNews = QtWidgets.QMainWindow()
    ui = Ui_LittleNews()
    ui.setupUi(LittleNews)
    LittleNews.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    # import nltk
    # nltk.download("punkt")
    main()