from datetime import date
from json import dumps, loads
from urllib2 import urlopen
from csv import DictReader
now = str(date.today())
url_list = ["http://finviz.com/export.ashx?v=111&f=ind_stocksonly,sh_price_o10,ta_change_u,ta_changeopen_u,ta_highlow20d_nh,ta_highlow50d_nh,ta_highlow52w_nh,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=4&o=-change",
            "http://finviz.com/export.ashx?v=111&f=fa_eps5years_pos,fa_epsqoq_pos,fa_epsyoy_pos,fa_epsyoy1_pos,fa_estltgrowth_pos,fa_sales5years_pos,fa_salesqoq_pos,ind_stocksonly,sh_avgvol_o50,sh_curvol_o0,sh_insiderown_o10,sh_instown_o10,sh_price_o10,ta_averagetruerange_o0.25,ta_beta_u1,ta_change_u,ta_changeopen_u,ta_highlow20d_nh,ta_highlow50d_nh,ta_highlow52w_nh,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=4"]


class Stock():
    def __init__(self, name="dummy", percent=-1.0, price=-1.0, date=now):
        self.name = name
        self.price = price
        self.growth = [percent]
        self.date = date
        self.current_streak = 0
        self.previous_streaks = {}

    def __str__(self):
        return self.name + "(" + str(self.current_streak) + "): " + str(self.price) +", "+ str(self.growth) + ", last up: " + self.date

    def up_today(self, date, percent, price):
        self.price = price
        self.growth.append(percent)
        self.current_streak += 1
        self.date = date

    def not_up_today(self):
        self.current_streak = 0
        self.previous_streaks[self.date] = self.growth
        self.date = None
        self.growth = []

    def dumps(self):
        return dumps(self.__dict__)

    def loads(self, input_string):
        stock_dictionary = loads(input_string)
        self.name = stock_dictionary["name"]
        self.price = stock_dictionary["price"]
        self.growth = stock_dictionary["growth"]
        self.date = stock_dictionary["date"]
        self.current_streak = stock_dictionary["current_streak"]
        self.previous_streaks = stock_dictionary["previous_streaks"]

stock_results = []
stocks_from_url_dict = {}
for url in url_list:
    up_text = urlopen(url)
    for row in DictReader(up_text):
        stocks_from_url_dict[row['Ticker']] = [row['Change'], row['Price']]

with open("/Users/lego90511/Desktop/stocks.txt", "r+") as new_stock_file:
    with open("/Users/lego90511/Desktop/stocks.txt", "r+") as old_stock_file:
        file_date = old_stock_file.readline()
        if file_date != now+"\n":
            new_stock_file.write(now)
            for line in old_stock_file:
                new_s = Stock()
                new_s.loads(line)
                stock_name = new_s.name
                if new_s.name in stocks_from_url_dict.keys():
                    new_s.up_today(now, stocks_from_url_dict[stock_name][0], stocks_from_url_dict[stock_name][1])
                    stocks_from_url_dict.pop(stock_name)
                else:
                    new_s.not_up_today()
                stock_results.append(new_s)
            for stock in stocks_from_url_dict.keys():
                new_s = Stock(stock, stocks_from_url_dict[stock][0], stocks_from_url_dict[stock][1])
                stock_results.append(new_s)
            stock_results.sort(key=lambda stock: stock.current_streak)
            for stock in stock_results:
                new_stock_file.write('\n'+stock.dumps())