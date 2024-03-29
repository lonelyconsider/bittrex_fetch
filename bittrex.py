# -*-coding: utf-8-*-

import requests
import pymssql
from config import server, user, password, database
import csv
from datetime import datetime, timedelta
from zimbrasmtp import SmtpServer

# datetime str
minute_str = datetime.now().strftime('%Y%m%d%H%M')  # CSV命名用
now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 取数据时间

# ETH到BTC汇率
ticker_url = "https://api.bittrex.com/api/v1.1/public/getticker?market=BTC-ETH"
eth_btc = requests.get(ticker_url).json()['result']['Ask']

summary_url = "https://api.bittrex.com/api/v1.1/public/getmarketsummaries"  # 取汇率用URL


def order_url_maker(coin_from, coin_to):
    """
    订单URL，根据币种变化
    :param coin_from:
    :param coin_to:
    :return:
    """
    order_url = "https://api.bittrex.com/api/v1.1/public/getorderbook?market={0}-{1}&type=both".format(coin_from, coin_to)
    return order_url


# 数据库连接
conn = pymssql.connect(server, user, password, database)
cursor = conn.cursor()


def get_all_markets():
    """
    取出所有B网支持的货币对
    """
    # 从数据库中查出所有需要的货币对
    cursor.execute("select Pair from IB_RPA.T_MST_PAIRS")
    pair_list = [pair[0] for pair in cursor]
    response = requests.get("https://api.bittrex.com/api/v1.1/public/getmarkets")
    if response.status_code == 200:
        result = response.json()['result']
        for rec in result:
            pair = rec['MarketCurrency'] + rec['BaseCurrency']
            if pair in pair_list:
                print(pair)


def get_summary():
    """
    取汇率到汇率表
    :return:
    """
    # 从数据库中查出所有需要的货币对
    cursor.execute("select Pair from IB_RPA.T_MST_PAIRS where BittrexTag = 'yes'")
    pair_list = [pair[0] for pair in cursor]

    # 从API取得数据
    response = requests.get(summary_url)
    if response.status_code == 200:
        # 创建csv文件
        f = open('Old\\BITTREX_RATE_{0}.csv'.format(minute_str), 'a', encoding='utf-8', newline='')
        writer = csv.writer(f)
        writer.writerow(['Vendor', 'Pair', 'AskRate', 'BidRate', '24hVolume', 'High', 'Low', 'Time',
                         'CreateDate', 'CreateUser'])
        result = response.json()['result']
        # 遍历API中所有货币对，如果在需要列表中则写入csv，然后写入数据库
        items = []
        for item in result:
            # API提供的时间戳字段
            time_str = (datetime.strptime(item['TimeStamp'].split('.')[0].replace('T', ' '), '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
            pair = item['MarketName'].split('-')[1]+item['MarketName'].split('-')[0]
            if pair in pair_list:
                items.append(('Bittrex', pair, '%.8f' % item['Ask'], '%.8f' % item['Bid'], '%.8f' % item['BaseVolume'], '%.8f' % item['High'],
                              '%.8f' % item['Low'], time_str, now_str, 'DA'))
        writer.writerows(items)
        f.close()

        # 写数据库
        try:
            cursor.executemany(
                "insert into IB_RPA.T_F_Bittrex_Rate (Vendor, Pair, AskRate, BidRate, [24hVolume], HighPrice, LowPrice,"
                "Time, CreateDate, CreateUser) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                items
            )
            conn.commit()
        except Exception as e:
            with open("insert_error.log", "a", encoding='utf-8') as f:
                f.write(now_str + ': ' + str(e))
            print('failed!')
            exit()
    else:
        with open("api_error.log", "a", encoding='utf-8') as f:
            f.write(now_str + ': ' + str(response.status_code) + response.text)
        print('failed!')
        exit()


def from_limit(pair, mid_rate, sell_items, buy_items, num):
    ask_limit, bid_limit, ask_depth, bid_depth, ask_span, bid_span = num, num, 0, 0, 0, 0  # init
    highest_ask, highest_bid, lowest_ask, lowest_bid = 0, 0, 0, 0
    ask_span = (sell_items[2][3] - mid_rate) / mid_rate
    bid_span = abs(buy_items[2][3] - mid_rate) / mid_rate
    ask_len, bid_len = len(sell_items), len(buy_items)
    if num > ask_len:  # 如果ask的订单不够
        pass
    else:
        # ask的两端rate
        highest_ask = sell_items[num-1][3]
        lowest_ask = sell_items[0][3]
        for i in range(num):
            # depth的币种是原币种（跟左边走）
            ask_depth = ask_depth + sell_items[i][4]  # * sell_items[i][3]
    if num > bid_len:  # 如果bid的订单不够
        pass
    else:    
        # bid的两端rate
        highest_bid = buy_items[0][3]
        lowest_bid = buy_items[num-1][3]
        for i in range(num):
            bid_depth = bid_depth + buy_items[i][4]   # * buy_items[i][3]
    return (
        'Bittrex', pair[0], 'limit', ask_limit, bid_limit, '%.8f' % ask_depth, '%.8f' % bid_depth, '%.3f' % ask_span,
        '%.3f' % bid_span, now_str, highest_ask, highest_bid, lowest_ask, lowest_bid
    )


def from_depth(pair, mid_rate, sell_items, buy_items, num):
    if pair[2] == 'ETH':
        depth = round(num / eth_btc, 8)  # num是BTC的数量，depth是真正币种的数量
    else:
        depth = num
    ask_limit, bid_limit, ask_depth, bid_depth, ask_span, bid_span = 0, 0, depth, depth, 0, 0  # init

    temp_depth = 0  # 累积depth
    for i in range(len(sell_items)):
        temp_depth = temp_depth + sell_items[i][4] * sell_items[i][3]
        if temp_depth >= depth:
            ask_limit = i + 1
            break
    # 如果将整个订单list遍历完毕还是没有达到所求depth，则limit=0
    if ask_limit == 0:
        highest_ask = 0
        lowest_ask = 0
    else:
        ask_span = (sell_items[ask_limit-1][3] - mid_rate) / mid_rate
        # ask的两端rate
        highest_ask = sell_items[ask_limit - 1][3]
        lowest_ask = sell_items[0][3]

    temp_depth = 0  # 累积depth
    for i in range(len(buy_items)):
        temp_depth = temp_depth + buy_items[i][4] * buy_items[i][3]
        if temp_depth >= depth:
            bid_limit = i + 1
            break
    if bid_limit == 0:
        highest_bid = 0
        lowest_bid = 0
    else:
        bid_span = abs(buy_items[bid_limit-1][3] - mid_rate) / mid_rate
        # bid的两端rate
        highest_bid = buy_items[0][3]
        lowest_bid = buy_items[bid_limit - 1][3]
    return (
        'Bittrex', pair[0], 'depth', ask_limit, bid_limit, ask_depth, bid_depth, '%.3f' % ask_span,
        '%.3f' % bid_span, now_str, highest_ask, highest_bid, lowest_ask, lowest_bid
    )


def from_span(pair, mid_rate, sell_items, buy_items, num):
    ask_limit, bid_limit, ask_depth, bid_depth, ask_span, bid_span = 0, 0, 0, 0, num, num  # init
    ask_rate = num * mid_rate + mid_rate  # 不可以超过ask_rate
    bid_rate = mid_rate - num * mid_rate  # 不可以低于mid_rate
    for i in range(len(sell_items)):
        if sell_items[i][3] > ask_rate:
            ask_limit = i
            break
        else:
            ask_depth = ask_depth + sell_items[i][4]  # * sell_items[i][3]
    if ask_limit == 0:
        ask_depth = 0
        highest_ask = 0
        lowest_ask = 0
    else:
        # ask的两端rate
        highest_ask = sell_items[ask_limit - 1][3]
        lowest_ask = sell_items[0][3]

    for i in range(len(buy_items)):
        if buy_items[i][3] < bid_rate:
            bid_limit = i
            break
        else:
            bid_depth = bid_depth + buy_items[i][4]  # * buy_items[i][3]
    if bid_limit == 0:
        bid_depth = 0
        highest_bid = 0
        lowest_bid = 0
    else:
        # bid的两端rate
        highest_bid = buy_items[0][3]
        lowest_bid = buy_items[bid_limit - 1][3]
    return (
        'Bittrex', pair[0], 'span', ask_limit, bid_limit, '%.8f' % ask_depth, '%.8f' % bid_depth, ask_span,
        bid_span, now_str, highest_ask, highest_bid, lowest_ask, lowest_bid
    )


def get_order():
    # 从数据库中查出所有需要的货币对（目前24个货币对）
    cursor.execute("select Pair, CoinFrom, CoinTo from IB_RPA.T_MST_PAIRS where BittrexTag = 'yes'")
    pair_list = [pair for pair in cursor]
    # test
    # pair_list = [('XRPETH', 'XRP', 'ETH')]
    for pair in pair_list:
        print(pair)
        order_url = order_url_maker(pair[2], pair[1])  # 对调方向去访问API
        response = requests.get(order_url)
        if response.status_code == 200:
            result = response.json()['result']
            buy_list = result['buy']
            sell_list = result['sell']
            items = []
            buy_items = []
            sell_items = []
            x, y = 0, 0
            for i in buy_list:
                temp = ('Bittrex', pair[0], 'bid', float('%.8f' % i['Rate']), float('%.8f' % i['Quantity']),
                        x, now_str, 'DA')
                items.append(temp)
                buy_items.append(temp)
                x = x + 1
            for i in sell_list:
                temp = ('Bittrex', pair[0], 'ask', float('%.8f' % i['Rate']), float('%.8f' % i['Quantity']),
                        y, now_str, 'DA')
                items.append(temp)
                sell_items.append(temp)
                y = y + 1

            try:
                # 写数据库
                cursor.executemany(
                    "insert into IB_RPA.T_F_Bittrex_Order (Vendor, Pair, Type, Price, Quantity, [No.], CreateDate,"
                    "CreateUser) values (%s, %s, %s, %s, %s, %s, %s, %s)",
                    items
                )
                conn.commit()
            except Exception as e:
                with open("insert_error.log", "a", encoding='utf-8') as f:
                    f.write(now_str + ': ' + str(e))
                print('failed!')
                exit()

            # 分析
            records = []
            mid_rate = (buy_items[0][3] + sell_items[0][3]) / 2  # 中心点
            records.append(from_limit(pair, mid_rate, sell_items, buy_items, 3))  # limit = 3
            records.append(from_limit(pair, mid_rate, sell_items, buy_items, 10))  # limit = 10
            records.append(from_limit(pair, mid_rate, sell_items, buy_items, 20))  # limit = 20
            records.append(from_depth(pair, mid_rate, sell_items, buy_items, 2))  # depth = 2
            records.append(from_depth(pair, mid_rate, sell_items, buy_items, 5))  # depth = 5
            records.append(from_depth(pair, mid_rate, sell_items, buy_items, 10))  # depth = 10
            records.append(from_span(pair, mid_rate, sell_items, buy_items, 0.001))  # span = 0.001
            records.append(from_span(pair, mid_rate, sell_items, buy_items, 0.003))  # span = 0.003
            records.append(from_span(pair, mid_rate, sell_items, buy_items, 0.005))  # span = 0.005
            records.append(from_span(pair, mid_rate, sell_items, buy_items, 0.007))  # span = 0.007
            # 写数据库
            cursor.executemany(
                "insert into IB_RPA.T_E_Bittrex_Order_Analysis (Vendor, Pair, IndependentVar, AskLimit, BidLimit, "
                "AskDepth, BidDepth, AskSpan, BidSpan, CreateDate, HighestAsk, HighestBid, LowestAsk, LowestBid) "
                "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                records
            )
            conn.commit()
        else:
            with open("error.log", "a", encoding='utf-8') as f:
                f.write(str(response.status_code) + response.text)
            print('failed!')


if __name__ == '__main__':
    try:
        import time
        start = time.time()
        # get_all_markets()
        get_summary()
        get_order()
        conn.close()
        end = time .time()
        print(end - start, 's')
    except Exception as e:
        print(e)
        smtp = SmtpServer()
        smtp.send_mail(subject='Bittrex-Remind',message='The data could not be get now, please check the API calls and DB setting.')
        exit()