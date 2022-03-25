import datetime
import re

class Timestamp(object):
    # Return today date as YYYY-MM-DD
    def get_date_now(self):
        today = datetime.date.today()
        return today
    
    # Remove "-" from stringdate
    def format_date(self, date="now"):
        if date == "now":
            today = datetime.date.today()
            fdate = today.strftime("%Y%m%d")
        else:
            date = datetime.date.fromisoformat(date)
            fdate = date.strftime("%Y%m%d")
        return fdate
    
    # Return list of date from start to stop as YYYY-MM-DD
    def timerange(self, isostart_date:"YYYY-MM-DD", isostop_date:"YYYY-MM-DD"):
        date_range = list()
        start_date = datetime.date.fromisoformat(isostart_date)
        stop_date = datetime.date.fromisoformat(isostop_date)
        if start_date <= stop_date:
            while start_date <= stop_date:
                date_range.append(str(start_date))
                start_date += datetime.timedelta(days=1)
            return date_range
        else:
            return -1

if __name__ == "__main__":
    tims = Timestamp()
    print(tims.format_date("2020-01-01"))
    # now = tims.timerange("2021-02-04", "2021-02-20")
    # date = "2020-12-31"
    # since_date = date
    # until_date = str(datetime.date.fromisoformat(date)+datetime.timedelta(days=1))
    # print(until_date)